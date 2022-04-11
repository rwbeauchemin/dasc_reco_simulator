import random
import math


def title_link(title_id):
    """(Deprecated) Creates a link to view more details on a title given an id

    Args:
        title_id (Any): The id to look up with

    Returns:
        str: The link to get more details on the title
    """
    # TODO: Find a good landing page to learn more about Peacock titles
    return f"https://www.themoviedb.org/movie/{title_id}"


def fetch_poster(title_id):
    """Creates a link to see an image of the title given an id

    Args:
        title_id (Any): The id to look up with

    Returns:
        str: The link to an image of the title
    """
    return (
        'https://imageservice.disco.peacocktv.com/uuid/'
        f'{title_id}/TITLE_ART_16_9/400'
        '?territory=US&proposition=NBCUOTT&language=eng')

def apply_shuffling(titles, title_number, shuffle_mode=None):
    """Shuffles using shuffling functions found in this utililty file.

    Args:
        titles (pd.Dataframe): A dataframe to apply shuffling to
        title_number (int): The number of titles to return
        shuffle_mode (str, optional): The type of . Defaults to None.

    Returns:
        pd.DataFrame: The dataframe with shuffling and truncation applied
    """
    if shuffle_mode is None or shuffle_mode == 'None':
        titles = titles.head(title_number)
    elif shuffle_mode == 'linear':
        indices = linear_rising_temperature(list(titles.index), break_at=title_number)
        titles = titles.loc[indices]
    elif shuffle_mode == 'log':
        indices = log_rising_temperature(list(titles.index), break_at=title_number)
        titles = titles.loc[indices]
    elif shuffle_mode == 'exp':
        indices = exponential_rising_temperature(list(titles.index), break_at=title_number)
        titles = titles.loc[indices]
    return titles


def exponential_rising_temperature(sorted_list: list,
                                   init_group: int = 4,
                                   break_at: int = 12):
    final_list = []
    group = init_group * 1
    for i in range(len(sorted_list)):
        selection = random.choice(sorted_list[:group])
        sorted_list.remove(selection)
        final_list.append(selection)
        group *= 2
        if i + 1 == break_at:
            break
    return final_list


def linear_rising_temperature(sorted_list: list,
                              init_temperature: int = 2,
                              break_at: int = 12):
    final_list = []
    temperature = init_temperature * 1
    for i in range(len(sorted_list)):
        selection = random.choice(sorted_list[:temperature])
        sorted_list.remove(selection)
        final_list.append(selection)
        temperature = (init_temperature + i) * 2
        if i + 1 == break_at:
            break
    return final_list


def log_rising_temperature(sorted_list: list,
                           init_temperature: int = 2,
                           break_at: int = 12):
    final_list = []
    temperature = init_temperature * 1
    for i in range(len(sorted_list)):
        selection = random.choice(sorted_list[:temperature])
        sorted_list.remove(selection)
        final_list.append(selection)
        temperature = 2 * math.ceil(math.log(init_temperature + i)) + 1
        if i + 1 == break_at:
            break
    return final_list
