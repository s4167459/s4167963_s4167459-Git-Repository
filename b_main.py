import pyhtml

import mission_statement
import focused_view_page_via_climate_metric
import deep_dive_page
import landing_page
import focused_view_page_via_weather_station
import similarity_chanage_in_metric_percentages_page

pyhtml.need_debugging_help = True

# Page routes
pyhtml.MyRequestHandler.pages["/"] = landing_page.landing_page
pyhtml.MyRequestHandler.pages["/m-statement"] = mission_statement
pyhtml.MyRequestHandler.pages["/focused-metric"] = focused_view_page_via_climate_metric
pyhtml.MyRequestHandler.pages["/deep-dive"] = deep_dive_page
pyhtml.MyRequestHandler.pages["/focused-station"] = focused_view_page_via_weather_station
pyhtml.MyRequestHandler.pages["/similarity"] = similarity_chanage_in_metric_percentages_page


# Host the site
pyhtml.host_site()
