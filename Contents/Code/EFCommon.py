import urllib2
from collections import OrderedDict

ROUTE_PREFIX =			'/video/efukt'

BASE_URL =			'https://efukt.com'
EF_VIDEO_SEARCH_URL =	BASE_URL + '/search/%s/'
EF_RANDOM_VIDEO_URL =	BASE_URL + '/random.php'

SORT_ORDERS = OrderedDict([
	('Most Recent',				BASE_URL + '/'),
	('Most Viewed - All Time',	BASE_URL + '/all-time/'),
	('Most Viewed - This Year',	BASE_URL + '/year/'),
	('Most Viewed - This Month',	BASE_URL + '/month/'),
	('Most Viewed - Today',		BASE_URL + '/today/'),
	('Favorites',				BASE_URL + '/favorites/')
])

MAX_VIDEOS_PER_PAGE =			20

@route(ROUTE_PREFIX + '/videos/browse')
def BrowseVideos(title='Browse Videos'):
	
	# Create a dictionary of menu items
	browseVideosMenuItems = OrderedDict()
	
	# Add the sorting options
	for sortTitle, sortURL in SORT_ORDERS.items():
		
		# Add a menu item for the category
		browseVideosMenuItems[sortTitle] = {'function':ListVideos, 'functionArgs':{'url':sortURL}}
	
	# Generate the menu with the sort orders
	oc = GenerateMenu(title, browseVideosMenuItems, no_cache=True)
	
	# Add an option for a random video
	oc.add(RandomVideo())
	
	return oc

@route(ROUTE_PREFIX + '/videos/list')
def ListVideos(title='List Videos', url=BASE_URL, page=1, pageLimit = MAX_VIDEOS_PER_PAGE):
	
	categoriesToIgnore =	["Gallery", "Plugs", "Advertisement"]

	# Create the object to contain all of the videos
	oc = ObjectContainer(title2 = title)
	
	# Add the page number into the URL
	pagedURL = url if page == 1 else url + str(page) + '/'
	
	# Get videos
	videos = SharedCodeService.EFCommon.GetVideos(pagedURL)
	
	# Loop through the videos in the page
	for video in videos:
		
		# Check for relative URLs
		if (video['url'].startswith('/')):
			video['url'] = BASE_URL + videoURL
		
		# Make sure the last step went smoothly (this is probably redundant but oh well), and also make sure it's not an external link or a gif
		if (video['url'].startswith(BASE_URL) and
			not video['category'] in categoriesToIgnore and
			not video['url'].startswith(BASE_URL + '/view.gif.php')):

			# Create a Video Clip Object for the video
			oc.add(VideoClipObject(
				url =		video['url'],
				title =		video['title'],
				thumb =		video['thumbnail'],
				summary =	video['summary']
			))
	
	# There is a slight change that this will break... If the number of videos returned in total is divisible by MAX_VIDEOS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(videos) == int(pageLimit)):
		oc.add(NextPageObject(
			key =	Callback(ListVideos, title=title, url=url, page = int(page)+1),
			title =	'Next Page'
		))

	return oc

@route(ROUTE_PREFIX + '/search')
def SearchVideos(query):
	
	# Format the query for use in PornHub's search
	formattedQuery = formatStringForSearch(query, "%20")
	
	try:
		return ListVideos(title='Search Results For ' + query, url=EF_VIDEO_SEARCH_URL % formattedQuery)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)

def RandomVideo():
	# This function follow the redirect at /random.php (EF_RANDOM_VIDEO_URL), and gets the redirected URL. Then returns a video object at that URL
	
	# Request the random video URL
	randomVideoRequest =		urllib2.Request(EF_RANDOM_VIDEO_URL, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0"})
	
	# Get the response from the request
	randomVideoResponse =	urllib2.urlopen(randomVideoRequest)
	
	# Return the video clip object
	return VideoClipObject(
		url =		randomVideoResponse.geturl(),
		title =	'Random'
	)

def GenerateMenu(title, menuItems, no_cache=False):
	# Create the object to contain the menu items
	oc = ObjectContainer(title2=title, no_cache=no_cache)
	
	# Loop through the menuItems dictionary
	for menuTitle, menuData in menuItems.items():
		# Create empty dictionaries to hold the arguments for the Directory Object and the Function
		directoryObjectArgs =	{}
		functionArgs =		{}
		
		# See if any Directory Object arguments are present in the menu data
		if ('directoryObjectArgs' in menuData):
			# Merge dictionaries
			directoryObjectArgs.update(menuData['directoryObjectArgs'])
		
		# Check to see if the menu item is a search menu item
		if ('search' in menuData and menuData['search'] == True):
			directoryObject = InputDirectoryObject(title=menuTitle, **directoryObjectArgs)
		# Check to see if the menu item is a next page item
		elif ('nextPage' in menuData and menuData['nextPage'] == True):
			directoryObject = NextPageObject(title=menuTitle, **directoryObjectArgs)
		# Otherwise, use a basic Directory Object
		else:
			directoryObject = DirectoryObject(title=menuTitle, **directoryObjectArgs)
			functionArgs['title'] = menuTitle
		
		# See if any Function arguments are present in the menu data
		if ('functionArgs' in menuData):
			# Merge dictionaries
			functionArgs.update(menuData['functionArgs'])
		
		# Set the Directory Object key to the function from the menu data, passing along any additional function arguments
		directoryObject.key =	Callback(menuData['function'], **functionArgs)
		
		# Add the Directory Object to the Object Container
		oc.add(directoryObject)
	
	return oc

# I stole this function (and everything I did for search basically) from the RedTube Plex Plugin, this file specifically https://github.com/flownex/RedTube.bundle/blob/master/Contents/Code/PCbfSearch.py
def formatStringForSearch(query, delimiter):
	query = String.StripTags(str(query))
	query = query.replace('%20',' ')
	query = query.replace('  ',' ')
	query = query.strip(' \t\n\r')
	query = delimiter.join(query.split())
	
	return query