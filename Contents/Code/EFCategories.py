from EFCommon import *

EF_CATEGORIES_LIST_URL =	BASE_URL + '/search/'
EF_CATEGORY_URL =		BASE_URL + '/category/%s/'

@route(ROUTE_PREFIX + '/categories')
def BrowseCategories(title='Browse Categories', url = EF_CATEGORIES_LIST_URL):
	
	# Create a dictionary of menu items
	browseCategoriesMenuItems = OrderedDict()
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of catgegories
	categories = html.xpath("//select[@name = 'cat']/option/text()")
	
	# Loop through all categories
	for category in categories:
		
		# Use xPath to extract category details
		categoryURL =		EF_CATEGORY_URL % category
		
		# Add a menu item for the category
		browseCategoriesMenuItems[category] = {'function':ListVideos, 'functionArgs':{'url':categoryURL}}
	
	return GenerateMenu(title, browseCategoriesMenuItems)