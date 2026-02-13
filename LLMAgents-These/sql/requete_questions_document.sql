WITH filtered_chunks AS (
        SELECT chunk_id
        FROM chunks
        WHERE document_id = '8a672d2ae6f2abfa4434e0f4145a9aa77bbc6d56'
    )
    SELECT
        q.question_id,
        q.content,
        q.status,
        q.difficulty_level,
        q.created_by,
        q.validated_by,
        qc.chunk_id
    FROM
        question_chunks qc
    JOIN
        questions q ON qc.question_id = q.question_id
    WHERE
        qc.chunk_id IN (SELECT chunk_id FROM filtered_chunks)