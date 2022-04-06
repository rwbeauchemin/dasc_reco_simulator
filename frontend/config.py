score_based_cfg = dict(
    title="Score Based",
    description="""
    This offers a simple score-based approach for all users.\n
    Some examples of scores could be:\n
    - Total National Views
    - Total Views in Users Region
    - The above two, but with a recency function applied\n
    and many more!
    """
)

content_based_kernel_cfg = dict(
    title="Content Based (Kernel)",
    description="""
    Content-based algorithms focus on particular titles watched by user.\n

    In this algorithm, a kernel function is established to estimate similarity.\n

    From the metadata we are extracting:
    - The first three listed actors
    - The director
    - Key words from the plot fields
    """
)

content_based_cosine_cfg = dict(
    title="Content Based (Cosine)",
    description="""
    Content-based algorithms focus on particular titles watched by user.\n

    This utilizes metadata such as:
    - Genre
    - Director
    - Description
    - Actors
    and more.\n

    In this algorithm, Cosine similarity is used between all fields in the titles.\n
    This is quick to calculate and is surprisingly accurate given good metadata.
    """
)
