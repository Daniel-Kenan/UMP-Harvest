import requests

def search_object_history(species_name):
    try:
        # Fetch data from Wikipedia API
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{species_name.replace(' ', '_')}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the request failed

        data = response.json()

        # Extract the title, description, and summary
        title = data.get('title', 'Unknown')
        description = data.get('description', 'No description available')
        summary = data.get('extract', 'No summary available')

        # Fetch page URL for more detailed information
        page_url = data.get('content_urls', {}).get('desktop', {}).get('page', 'No URL available')

        # Format the results as a string
        result = (
            f"<p>Title: {title}\n"
            f"Description: {description}\n"
            f"Summary: {summary}\n"
            f"More Information: {page_url} </p>"
        )

    except requests.exceptions.RequestException as e:
        result = f"Error: Could not retrieve data for {species_name}. Reason: {e}"

    return result

# # Example Usage
# species_name = "pig"
# result = search_object_history(species_name)
# print(result)
