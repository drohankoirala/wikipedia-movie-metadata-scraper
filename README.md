# Wikipedia Movie Metadata Scraper

### Overview
The Wikipedia Movie Metadata Scraper is a Python-based project designed to extract and compile detailed metadata about movies from Wikipedia pages. Utilizing libraries such as requests, lxml, colorama, and re, this scraper efficiently gathers information including IMDb IDs, movie genres, cast details, and various other attributes listed in Wikipedia's infobox tables.

### Features
1) IMDb ID Extraction:
   - Extracts the IMDb ID from Wikipedia pages by identifying and parsing the appropriate URL.
   - Saves the IMDb ID along with associated metadata such as the Wikipedia URL and poster image.
  
2) Genre Extraction:
   - Parses the text to identify and extract the genres of the film mentioned in the Wikipedia article.
  
3) Table Data Extraction:
   - Extracts key movie details from the Wikipedia infobox, such as release dates, running time, budget, box office, production companies, and more.
   - Uses regular expressions to clean and format the extracted data for consistency.

4) Cast Data Extraction:
   - Identifies and extracts the cast list from the Wikipedia page.
   - Extracts actor names, roles, and links to their Wikipedia pages
   - Organizes cast information, linking actors to their respective roles in the movie.
  
### Usage
- Define a list of Wikipedia movie URLs in the urls list.
- Instantiate the Scraper class.
- Iterate over the list of URLs, using the decode_page method to extract and print the metadata.

  ```
  urls = []  # list of URLs to fetch metadata from
  
  if __name__ == "__main__":
      scraper = Scraper()
      for url in urls:
          scraper.decode_page(scraper.decode_url(url))
      print(scraper.meta)
      print(scraper.character)```

### Applications
This project can be used for:
- Building a database of movie metadata for research or entertainment purposes.
- Integrating with other movie-related applications or services that require detailed metadata.
- Enhancing movie recommendation systems by providing comprehensive information.

### Notes
The project includes robust error handling to manage exceptions during data extraction.
Regular expressions are used extensively to ensure accurate and clean data extraction from the HTML content.
This project showcases a practical application of web scraping and data extraction techniques using Python, providing a valuable tool for anyone needing detailed and structured movie metadata from Wikipedia.
