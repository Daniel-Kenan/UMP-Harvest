import requests

def search_object_history(species_name):
    try:
        # Fetch data from Wikipedia API
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{species_name.replace(' ', '_')}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the request failed

        data = response.json()

        # Extract the title, description, summary, and image
        title = data.get('title', 'Unknown')
        description = data.get('description', 'No description available')
        summary = data.get('extract', 'No summary available')
        page_url = data.get('content_urls', {}).get('desktop', {}).get('page', 'No URL available')
        
        # Extract image URL if available
        image_url = data.get('thumbnail', {}).get('source', None)

        # Format the results as a string with <p> tags
        result = (
            f"<p>Title: {title}<br>"
            f"Description: {description}<br>"
            f"Summary: {summary}<br>"
            f"More Information: <a href='{page_url}'>{page_url}</a></p>"
        )

    except requests.exceptions.RequestException as e:
        result = f"<p>Error: Could not retrieve data for {species_name}. Reason: {e}</p>"
        image_url = None

    return result, image_url

# # Example Usage
# species_name = "pig"
# result, image_url = search_object_history(species_name)
# print(result)
# if image_url:
#     print(f"Image URL: {image_url}")
