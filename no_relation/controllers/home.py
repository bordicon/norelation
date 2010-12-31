import logging

from pylons import request, response, session, tmpl_context as context, url
from pylons.controllers.util import abort, redirect

from no_relation.lib.base import BaseController, render

log = logging.getLogger(__name__)

class HomeController(BaseController):
  def index(self):
    context.sets = [{
      'title': 'Sales',
      'stereotypes': [{
        'title': 'Customer',
      },{
        'title': 'Sale', 
      }]
    }]

    return render('home_index.html')
