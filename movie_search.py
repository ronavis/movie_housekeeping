import requests
import wikipedia
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import wikipediaapi

API_KEY = "04af73d659187b2cb1b8496ce77c1562"
OMDb_API_KEY = "eede0f57"
USER_AGENT = "MyApp/0.0.1" # Example user agent

def get_home_media_section(title, release_year=None):
    user_agent = "MovieHousekeeping/1.0 (Contact: ronavis.com)"
    wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=user_agent)

    # Try fetching the page with the original title first
    page = wiki_wiki.page(title)
    section = page.section_by_title('Home media')
    if section:
        return section.text

    # If the release year is provided, try fetching the page with the title formatted as "Title (YYYY_film)"
    if release_year:
        formatted_title = f"{title} ({release_year}_film)"
        page = wiki_wiki.page(formatted_title)
        section = page.section_by_title('Home media')
        if section:
            return section.text

    # Try fetching the page with underscores replacing spaces in the title
    underscore_title = title.replace(' ', '_')
    page = wiki_wiki.page(underscore_title)
    section = page.section_by_title('Home media')
    if section:
        return section.text

    # Return None if no section is found
    return None


def parse_home_media_section(text):
    if not text:
        return None

    formats = ['VHS', 'LaserDisc', 'DVD', 'Blu-ray', 'Ultra HD Blu-ray']
    parsed_data = {format: [] for format in formats}

    for format in formats:
        # Splitting the text into sentences, excluding "No." as a sentence delimiter
        sentences = re.split(r'(?<!No)\.', text)
        for sentence in sentences:
            if format in sentence:
                details = sentence.replace(format, '', 1).strip() + '.'
                parsed_data[format].append(details)

    return parsed_data

def print_parsed_data(parsed_data):
    if not parsed_data:
        print("Home media section not found.")
        return

    for format, details_list in parsed_data.items():
        if details_list:
            print(f"{format}:")
            for details in details_list:
                print(f"  {details}")
            print()

def get_movie_home_media_info(movie_title, release_date):
    print(f"Home media information for {movie_title}:")
    release_year = release_date.split('-')[0] if release_date else None
    home_media_content = get_home_media_section(movie_title, release_year)  # Include the release year
    parsed_data = parse_home_media_section(home_media_content)
    print_parsed_data(parsed_data)


def get_production_section(soup):
    if soup is None:
        return "No Wikipedia page found for this movie."
    heading_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    production_tag = None
    for tag in heading_tags:
        if 'Production' in tag.text:
            production_tag = tag

    # If there is no 'Production' section, return a message saying so
    if production_tag is None:
        return "No 'Production' section found on the Wikipedia page for this movie."

    # The content of the 'Production' section is contained in the following 'p' (paragraph) tags.
    # We'll find all the 'p' tags that follow the 'Production' tag and extract their text content.
    production_text = ""
    for sibling in production_tag.find_next_siblings():
        if sibling.name == 'p':
            production_text += sibling.text + '\n'
        elif sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Stop when we reach the next heading tag (i.e., the next section)
            break

    return production_text
def get_rotten_tomatoes_review(movie_name):
    # Format the movie name for the URL (replace spaces with underscores)
    movie_name = movie_name.replace(' ', '_').lower()

    # Send a request to the website
    r = requests.get(f"https://www.rottentomatoes.com/m/{movie_name}")

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(r.content, 'html.parser')

    # Find the critic consensus
    consensus = soup.find('span', {'data-qa': 'critics-consensus'})

    if consensus:
        return consensus.text.strip()
    else:
        return None
    
API_KEY = "04af73d659187b2cb1b8496ce77c1562"
OMDb_API_KEY = "eede0f57"  # Your OMDb API key here

def get_tmdb_movie_results(movie_name):
    base_url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': API_KEY,
        'query': movie_name
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if 'results' in data:
        return data['results']
    else:
        return None

def get_tmdb_movie_release_date(movie_name):
    movie_results = get_tmdb_movie_results(movie_name)
    if movie_results:
        release_date = movie_results[0]['release_date']
        return release_date
    else:
        return None

def get_week_number(release_date):
    date_object = datetime.strptime(release_date, '%Y-%m-%d')
    week_number = date_object.isocalendar()[1]
    return week_number

def get_box_office_data(year, week_number):
    base_url = f'https://www.boxofficemojo.com/weekend/{year}W{week_number}'
    try:
        tables = pd.read_html(base_url)
        if tables:
            box_office_data = tables[0]
            return box_office_data
        else:
            return None
    except:
        return None


def get_movie_details(movie_name):
    movie_results = get_tmdb_movie_results(movie_name)
    if not movie_results:
        return None

    print("Search Results:")
    for i, movie_info in enumerate(movie_results):
        print(f"{i+1}. {movie_info['title']} ({movie_info['release_date']})")

    choice = int(input("Enter the number corresponding to the correct movie: "))
    if choice < 1 or choice > len(movie_results):
        print("Invalid choice. Please try again.")
        return None

    selected_movie = movie_results[choice - 1]
    movie_id = selected_movie['id']
    base_url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    params = {
        'api_key': API_KEY
    }
    response = requests.get(base_url, params=params)
    movie_details = response.json()

    return movie_details
def calculate_age_at_release(birth_date, release_date):
    birth_date_object = datetime.strptime(birth_date, '%Y-%m-%d')
    release_date_object = datetime.strptime(release_date, '%Y-%m-%d')
    age_at_release = release_date_object.year - birth_date_object.year - ((release_date_object.month, release_date_object.day) < (birth_date_object.month, birth_date_object.day))
    return age_at_release

def get_person_birth_date(person_id):
    base_url = f'https://api.themoviedb.org/3/person/{person_id}'
    params = {
        'api_key': API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if 'birthday' in data and data['birthday']:
        return data['birthday']
    else:
        return None

def get_cast_details(movie_id, release_date):
    base_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits'
    params = {
        'api_key': API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if 'cast' in data:
        cast = data['cast']
        cast_details = []
        for cast_member in cast[:8]:
            cast_member_id = cast_member['id']
            cast_member_name = cast_member['name']
            cast_member_character = cast_member['character']
            cast_member_birth_date = get_person_birth_date(cast_member_id)
            if cast_member_birth_date:
                cast_member_age_at_release = calculate_age_at_release(cast_member_birth_date, release_date)
            else:
                cast_member_age_at_release = None
            cast_details.append((cast_member_name, cast_member_character, cast_member_age_at_release, cast_member_id))
        return cast_details
    else:
        return None
def get_person_movie_credits(person_id, release_date):
    base_url = f'https://api.themoviedb.org/3/person/{person_id}/movie_credits'
    params = {
        'api_key': API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if 'cast' in data:
        previous_movies = [movie for movie in data['cast'] if movie['release_date'] and movie['release_date'] < release_date and movie['character']]
        previous_movies.sort(key=lambda movie: movie['release_date'])
        last_5_movies = previous_movies[-5:]
        movie_details = []
        for movie in last_5_movies:
            movie_title = movie['title']
            movie_character = movie['character']
            movie_release_date = movie['release_date']
            movie_release_year = datetime.strptime(movie_release_date, '%Y-%m-%d').year
            person_birth_date = get_person_birth_date(person_id)
            if person_birth_date:
                person_age_at_release = calculate_age_at_release(person_birth_date, movie_release_date)
            else:
                person_age_at_release = None
            movie_details.append((movie_title, movie_character, person_age_at_release, movie_release_year))
        return movie_details
    else:
        return None

def get_person_next_movie_credits(person_id, release_date):
    base_url = f'https://api.themoviedb.org/3/person/{person_id}/movie_credits'
    params = {
        'api_key': API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if 'cast' in data:
        next_movies = [movie for movie in data['cast'] if movie['release_date'] and movie['release_date'] > release_date and movie['character']]
        next_movies.sort(key=lambda movie: movie['release_date'])
        next_5_movies = next_movies[:5]
        movie_details = []
        for movie in next_5_movies:
            movie_title = movie['title']
            movie_character = movie['character']
            movie_release_date = movie['release_date']
            movie_release_year = datetime.strptime(movie_release_date, '%Y-%m-%d').year
            person_birth_date = get_person_birth_date(person_id)
            if person_birth_date:
                person_age_at_release = calculate_age_at_release(person_birth_date, movie_release_date)
            else:
                person_age_at_release = None
            movie_details.append((movie_title, movie_character, person_age_at_release, movie_release_year))
        return movie_details
    else:
        return None
def get_omdb_movie_details(movie_name):
    base_url = 'http://www.omdbapi.com/'
    params = {
        'apikey': "eede0f57",  # Your OMDb API key here
        't': movie_name
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    # Extract Rotten Tomatoes rating
    ratings = data.get('Ratings', [])
    for rating in ratings:
        if rating['Source'] == 'Rotten Tomatoes':
            data['RottenTomatoes'] = rating['Value']
            break

    return data

def get_crew_details(movie_id):
    base_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits'
    params = {'api_key': API_KEY}
    response = requests.get(base_url, params=params)
    data = response.json()

    if 'crew' in data:
        crew = data['crew']
        directors = [member for member in crew if member['job'] == 'Director']
        producers = [member for member in crew if member['job'] in ['Producer', 'Executive Producer']]
        writers = [member for member in crew if member['job'] in ['Screenplay', 'Writer', 'Story']]

        return directors, producers, writers
    else:
        return [], [], []
    
def main():
    movie_name = input("Enter a movie name: ")

    # Fetch movie details from TMDB
    movie_details = get_movie_details(movie_name)
    if not movie_details:
        print(f"Movie '{movie_name}' not found.")
        return

    print(f"\n{movie_details['title']}")
    print(f"Release Date: {movie_details['release_date']}")
    omdb_movie_details = get_omdb_movie_details(movie_name)
    print(f"Rotten Tomatoes Score: {omdb_movie_details.get('RottenTomatoes', 'N/A')}")
    rotten_tomatoes_review = get_rotten_tomatoes_review(movie_name)
    print(f"Rotten Tomatoes Review: {rotten_tomatoes_review}")

    # Extract the release year from the release date
    release_year = movie_details['release_date'].split('-')[0]

    # Call get_movie_home_media_info() and pass the full movie title and release year
    get_movie_home_media_info(movie_details['title'], release_year)

    print(f"Runtime: {movie_details['runtime']} minutes")
    print(f"Film Budget: ${movie_details['budget']:,}")
    if 'BoxOffice' in omdb_movie_details and omdb_movie_details['BoxOffice'] != 'N/A':
        print(f"Total Box Office Gross: {omdb_movie_details['BoxOffice']}")

    year, month, day = map(int, movie_details['release_date'].split('-'))
    week_number = get_week_number(movie_details['release_date'])
    box_office_data = get_box_office_data(year, week_number)

    if box_office_data is not None:
        box_office_data = box_office_data.drop(['New This Week', 'Estimated'], axis=1)
        box_office_movie_data = box_office_data.loc[box_office_data['Release'].str.contains(movie_name, case=False)]
        if not box_office_movie_data.empty:
            print(f"\nBox Office Weekend Debut: {box_office_movie_data['Gross'].values[0]}")
            box_office_distributor = box_office_movie_data['Distributor'].values[0]
        else:
            box_office_distributor = None
    else:
        box_office_distributor = None
        
    if box_office_data is not None:
        box_office_data_str = str(box_office_data)
        box_office_data_str = '\n'.join(box_office_data_str.split('\n')[:-1])
        top_10_box_office_data_str = '\n'.join(box_office_data_str.split('\n')[:11])
        print(f"\nTop 10 Movies for the Weekend:\n{top_10_box_office_data_str}")

    cast_details = get_cast_details(movie_details['id'], movie_details['release_date'])
    if cast_details:
        print("\nTop Billed Cast:")
        for name, character, age_at_release, person_id in cast_details:
            print(f"\nActor: {name}")
            print(f"Role: {character}")
            if age_at_release is not None:
                print(f"Age at Release: {age_at_release}")
            else:
                print("Age at Release: Unknown")

            last_5_projects = get_person_movie_credits(person_id, movie_details['release_date'])
            if last_5_projects:
                print(f"\nLast 5 Projects Before {movie_details['title']}:")
                for project_title, project_role, project_age, project_year in last_5_projects:
                    print(f"- {project_title}, Role: {project_role}, Age: {project_age}, Release Year: {project_year}")

            next_5_projects = get_person_next_movie_credits(person_id, movie_details['release_date'])
            if next_5_projects:
                print(f"\nNext 5 Projects After {movie_details['title']}:")
                for project_title, project_role, project_age, project_year in next_5_projects:
                    print(f"- {project_title}, Role: {project_role}, Age: {project_age}, Release Year: {project_year}")

            print()
    directors, producers, writers = get_crew_details(movie_details['id'])
    for crew_role, crew_members in zip(["Directors", "Producers", "Writers"], [directors, producers, writers]):
        if crew_members:
            print(f"\n{crew_role}:")
            for member in crew_members:
                print(f"\n{member['name']}")
                person_id = member['id']
                last_5_projects = get_person_movie_credits(person_id, movie_details['release_date'])
                if last_5_projects:
                    print(f"\nLast 5 Projects Before {movie_details['title']}:")
                    for project_title, project_role, project_age, project_year in last_5_projects:
                        print(f"- {project_title}, Role: {project_role}, Age: {project_age}, Release Year: {project_year}")

                next_5_projects = get_person_next_movie_credits(person_id, movie_details['release_date'])
                if next_5_projects:
                    print(f"\nNext 5 Projects After {movie_details['title']}:")
                    for project_title, project_role, project_age, project_year in next_5_projects:
                        print(f"- {project_title}, Role: {project_role}, Age: {project_age}, Release Year: {project_year}")

                print()
    # Replace character names in the synopsis with the character name and the actor's name in parentheses:
    synopsis = movie_details['overview']
    for name, character, _, _ in cast_details:
        synopsis = synopsis.replace(character, f"{character} ({name})")
    print(f"\nBrief Synopsis: {synopsis}")

# Start the program:
if __name__ == "__main__":
    main()