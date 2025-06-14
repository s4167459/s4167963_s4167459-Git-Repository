import pyhtml

import mission_statement
import focused_view_page
import deep_dive_page

pyhtml.need_debugging_help = True

# Page routes
pyhtml.MyRequestHandler.pages["/m-statement"] = mission_statement
pyhtml.MyRequestHandler.pages["/focused"] = focused_view_page
pyhtml.MyRequestHandler.pages["/deep-dive"] = deep_dive_page

# Host the site
pyhtml.host_site()
