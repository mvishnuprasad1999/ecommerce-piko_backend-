from sqlalchemy import text
from src.search.embeddings import get_embedding
from src.search.groq_llm import parse_query

def search_products(db, query: str):
    parsed = parse_query(query)
    print("Parsed query:", parsed)

    keywords = parsed.get("keywords", "").strip()
    if isinstance(keywords, list):
        keywords = " ".join(keywords)

    max_price   = parsed.get("max_price")
    min_price   = parsed.get("min_price")
    min_stock   = parsed.get("min_stock")
    max_stock   = parsed.get("max_stock")
    expiry_days = parsed.get("expiry_days")
    category    = parsed.get("category")

    is_filter_only = not keywords

    def build_filters(params):
        filter_sql = ""

        if category:
            filter_sql += """ AND (
                LOWER(category) = LOWER(:category) OR
                LOWER(category) LIKE LOWER(:category_like)
            )"""
            params["category"] = category
            params["category_like"] = f"%{category}%"

        if max_price:
            filter_sql += " AND selling_price <= :max_price"
            params["max_price"] = float(max_price)

        if min_price:
            filter_sql += " AND selling_price >= :min_price"
            params["min_price"] = float(min_price)

        if min_stock is not None and max_stock is not None and min_stock == max_stock:
            filter_sql += " AND stock = :exact_stock"
            params["exact_stock"] = int(min_stock)
        else:
            if min_stock:
                filter_sql += " AND stock >= :min_stock"
                params["min_stock"] = int(min_stock)
            if max_stock:
                filter_sql += " AND stock <= :max_stock"
                params["max_stock"] = int(max_stock)

        if expiry_days:
            filter_sql += " AND TO_DATE(expiry_date, 'YYYY-MM-DD') <= CURRENT_DATE + (:expiry_days || ' days')::INTERVAL"
            params["expiry_days"] = str(int(expiry_days))

        return filter_sql, params

    def run_query(sql, params):
        result = db.execute(text(sql), params)
        rows = result.fetchall()
        keys = result.keys()
        return [dict(zip(keys, row)) for row in rows]

    # ─────────────────────────────────────────
    # FILTER ONLY (price/stock/expiry — no keywords)
    # ─────────────────────────────────────────
    if is_filter_only:
        print("Filter-only search")
        params = {}
        filter_sql, params = build_filters(params)

        sql = f"""
        SELECT id, name, description, category, mrp, selling_price,
               expiry_date, stock, product_imge_url, is_bought, is_wishlist
        FROM products
        WHERE is_bought = false
        {filter_sql}
        ORDER BY selling_price ASC, stock DESC
        LIMIT 20
        """
        results = run_query(sql, params)
        print(f"Filter-only results: {len(results)}")
        return results

    # ─────────────────────────────────────────
    # KEYWORD SEARCH — 5 levels like Amazon
    # ─────────────────────────────────────────
    query_embedding = get_embedding(keywords)
    embedding_str = str(query_embedding)

    base_select = """
    SELECT id, name, description, category, mrp, selling_price,
           expiry_date, stock, product_imge_url, is_bought, is_wishlist,
           embedding <-> CAST(:embedding AS vector) AS similarity
    FROM products
    WHERE is_bought = false
    """

    # ── LEVEL 1: Exact name match ──────────────
    print("Level 1: Exact name match")
    params = {"embedding": embedding_str}
    filter_sql, params = build_filters(params)

    sql = f"""
    SELECT id, name, description, category, mrp, selling_price,
           expiry_date, stock, product_imge_url, is_bought, is_wishlist,
           0.0 AS similarity
    FROM products
    WHERE is_bought = false
    AND LOWER(name) = LOWER(:exact_name)
    {filter_sql}
    LIMIT 20
    """
    params["exact_name"] = keywords
    results = run_query(sql, params)

    if results:
        print(f"Level 1 found: {len(results)}")
        return results

    # ── LEVEL 2: Name/description/category contains keywords ──
    print("Level 2: Name/description/category contains keywords")
    params = {"embedding": embedding_str}
    filter_sql, params = build_filters(params)

    sql = f"""
    SELECT id, name, description, category, mrp, selling_price,
           expiry_date, stock, product_imge_url, is_bought, is_wishlist,
           embedding <-> CAST(:embedding AS vector) AS similarity
    FROM products
    WHERE is_bought = false
    AND (
        LOWER(name) LIKE LOWER(:name_like) OR
        LOWER(description) LIKE LOWER(:name_like) OR
        LOWER(category) LIKE LOWER(:name_like)
    )
    {filter_sql}
    ORDER BY similarity ASC, stock DESC, selling_price ASC
    LIMIT 20
    """
    params["name_like"] = f"%{keywords}%"
    results = run_query(sql, params)

    if results:
        print(f"Level 2 found: {len(results)}")
        return results

    # ── LEVEL 3: Category + strict similarity ──
    print("Level 3: Category + strict similarity < 1.2")
    params = {"embedding": embedding_str}
    filter_sql, params = build_filters(params)

    sql = f"""
    {base_select}
    AND embedding <-> CAST(:embedding AS vector) < 1.2
    {filter_sql}
    ORDER BY similarity ASC, stock DESC, selling_price ASC
    LIMIT 20
    """
    results = run_query(sql, params)

    if results:
        print(f"Level 3 found: {len(results)}")
        return results

    # ── LEVEL 4: Loose similarity ──────────────
    print("Level 4: Loose similarity < 1.5")
    params = {"embedding": embedding_str}
    filter_sql, params = build_filters(params)

    sql = f"""
    {base_select}
    AND embedding <-> CAST(:embedding AS vector) < 1.5
    {filter_sql}
    ORDER BY similarity ASC, stock DESC, selling_price ASC
    LIMIT 20
    """
    results = run_query(sql, params)

    if results:
        print(f"Level 4 found: {len(results)}")
        return results

    # ── LEVEL 5: No threshold fallback ─────────
    print("Level 5: No threshold fallback")
    params = {"embedding": embedding_str}
    filter_sql, params = build_filters(params)

    sql = f"""
    {base_select}
    {filter_sql}
    ORDER BY similarity ASC, stock DESC, selling_price ASC
    LIMIT 10
    """
    results = run_query(sql, params)
    print(f"Level 5 found: {len(results)}")
    return results