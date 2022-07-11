import xbmc

def setup_xml(api_key=None, latitude=None,longitude=None,xml_path=None):
	import requests, json
	from math import cos, asin, sqrt

	def distance(lat1, lon1, lat2, lon2):
		p = 0.017453292519943295
		hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
		return 12742 * asin(sqrt(hav))



	sitelist = requests.get('http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/json/sitelist?res=hourly&key=%s' % (api_key)).json()

	my_lat = latitude
	my_long = longitude

	sitelist2 = []
	for i in sitelist['Locations']['Location']:
		i['distance_from_me'] = distance(my_lat, my_long, float(i['latitude']), float(i['longitude']))
		sitelist2.append(i)
		#print(i)


	newlist = sorted(sitelist2, key=lambda d: d['distance_from_me']) 
	x = 0
	for i in newlist:
		#print(i)
		if x == 0:
			obs_1 = i
		if x == 1:
			obs_2 = i
			break
		x = x + 1
		


	sitelist3 = requests.get('http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?res=daily&key=%s' % (api_key)).json()


	sitelist4 = []
	for i in sitelist3['Locations']['Location']:
		i['distance_from_me'] = distance(my_lat, my_long, float(i['latitude']), float(i['longitude']))
		sitelist4.append(i)
		#print(i)


	newlist = sorted(sitelist4, key=lambda d: d['distance_from_me']) 
	x = 0
	for i in newlist:
		#print(i)
		if x == 0:
			forecast_1 = i
		if x == 1:
			forecast_2 = i
			break
		x = x + 1

	sitelist5 = requests.get('http://datapoint.metoffice.gov.uk/public/data/txt/wxfcs/regionalforecast/json/sitelist?key=%s' % (api_key)).json()


	regions = {}
	regions['os'] = {'name': 'Orkney and Shetland'}
	regions['he'] = {'name': 'Highland and Eilean Siar'}
	regions['gr'] = {'name': 'Grampian'}
	regions['ta'] = {'name': 'Tayside'}
	regions['st'] = {'name': 'Strathclyde'}
	regions['dg'] = {'name': 'Dumfries, Galloway, Lothian'}
	regions['ni'] = {'name': 'Northern Ireland'}
	regions['yh'] = {'name': 'Yorkshire and the Humber'}
	regions['ne'] = {'name': 'Northeast England'}
	regions['em'] = {'name': 'East Midlands'}
	regions['ee'] = {'name': 'East of England'}
	regions['se'] = {'name': 'London and Southeast England'}
	regions['nw'] = {'name': 'Northwest England'}
	regions['wm'] = {'name': 'West Midlands'}
	regions['sw'] = {'name': 'Southwest England'}
	regions['wl'] = {'name': 'Wales'}
	regions['uk'] = {'name': 'United Kingdom'}

	for i in sitelist5['Locations']['Location']:
		regions[i['@name']]['id'] = i['@id']

	if 1==1:
		print(forecast_1, 'forecast_1')
		print(regions[forecast_1['region']], 'forecast_1')
		print('')
		print(forecast_2, 'forecast_2')
		print(regions[forecast_2['region']], 'forecast_2')
		print('')
		print(obs_1, 'obs_1')
		print(regions[obs_1['region']], 'obs_1')
		print('')
		print(obs_2, 'obs_2')
		print(regions[obs_2['region']], 'obs_2')
		print('')




	import xml.etree.cElementTree as ET

	settings = ET.Element("settings", version="2")

	ET.SubElement(settings, "setting", id="ApiKey").text = api_key
	ET.SubElement(settings, "setting", id="EraseCache", default="true").text = "false"
	ET.SubElement(settings, "setting", id="ForecastLocation").text = forecast_1['name']
	ET.SubElement(settings, "setting", id="ForecastLocationID").text = forecast_1['id']
	ET.SubElement(settings, "setting", id="ForecastLocationLatitude", default="true").text = forecast_1['latitude']
	ET.SubElement(settings, "setting", id="ForecastLocationLongitude", default="true").text = forecast_1['longitude']
	ET.SubElement(settings, "setting", id="GeoIPProvider", default="true").text = "0"
	ET.SubElement(settings, "setting", id="GeoLocation").text = "false"
	ET.SubElement(settings, "setting", id="ObservationLocation1").text = obs_2['name']
	ET.SubElement(settings, "setting", id="ObservationLocation").text = obs_1['name']
	ET.SubElement(settings, "setting", id="ObservationLocationID1").text = obs_2['id']
	ET.SubElement(settings, "setting", id="ObservationLocationID").text = obs_1['id']
	ET.SubElement(settings, "setting", id="RegionalLocation1").text = regions[obs_2['region']]['name']
	ET.SubElement(settings, "setting", id="RegionalLocation").text = regions[obs_1['region']]['name']
	ET.SubElement(settings, "setting", id="RegionalLocationID").text = regions[obs_1['region']]['id']

	tree = ET.ElementTree(settings)
	xml_str2 = ET.tostring(settings)
	print(xml_str2)


	def prettify(elem):
		#from xml.etree import ElementTree
		from xml.dom import minidom
		"""Return a pretty-printed XML string for the Element.
			Use either TREE or XML tostring output
		"""
		try:
			try: rough_string = ET.tostring(elem, 'utf-8')
			except: rough_string = elem
			reparsed = minidom.parseString(rough_string)
			return reparsed.toprettyxml(indent="\t", newl="\n", encoding="utf-8")
		except:
			elem = elem.getroot()
			elem = ET.tostring(elem)
			elem= ET.fromstring(elem)
			rough_string = ET.tostring(elem)
			reparsed = minidom.parseString(rough_string)
			return reparsed.toprettyxml(indent="\t", newl="\n", encoding="utf-8")

	xml_tree = prettify(tree)
	try: xml_tree = xml_tree.replace('<?xml version="1.0" ?>\n','')
	except: xml_tree = xml_tree.decode('utf-8').replace('<?xml version="1.0" encoding="utf-8"?>\n','')

	f = open(xml_path, "w")
	f.write(xml_tree)
	f.close()
	return xml_path