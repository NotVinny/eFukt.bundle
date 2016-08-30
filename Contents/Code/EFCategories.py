from EFCommon import *

EF_CATEGORIES_LIST_URL =	BASE_URL + '/search/'
EF_CATEGORY_URL =		BASE_URL + '/category/%s/'

@route(ROUTE_PREFIX + '/categories')
def BrowseCategories(title='Browse Categories', url = EF_CATEGORIES_LIST_URL):
	
	# Create a dictionary of menu items
	browseCategoriesMenuItems = OrderedDict()
	
	# Get catgegories
	categories = SharedCodeService.EFCommon.GetCategories(url)
	
	# Loop through all categories
	for category in categories:
		
		# Add a menu item for the category
		browseCategoriesMenuItems[category] = {
			'function':		ListVideos,
			'functionArgs':	{'url':EF_CATEGORY_URL % category}
		}
	
	return GenerateMenu(title, browseCategoriesMenuItems)