#!/usr/bin/env python

# Python 2/3 compatibility
from __future__ import (print_function, unicode_literals, division)
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

__metaclass__ = type


import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

from IPython.display import display, HTML

import json
import pandas as pd
#pd.options.display.mpl_style = 'default' 

from pprint import pprint


def ga():
    service = initialize_service()
    return service.data().ga()

def get_df(heading=None, **kwargs):
    service = initialize_service()
    result = service.data().ga().get(**kwargs).execute()
    df = results_wrapper(result, heading=heading)
    return df

def get_one(**kwargs):
    service = initialize_service()
    result = service.data().ga().get(**kwargs).execute()
    df = results_wrapper(result)
    if len(df.index) == 1 and len(df.columns) == 1:
        return df.iloc[0,0]
    else:
        raise ValueError(("result should contain just one value\n\n",
                         str(result)))


def scalar_type_sniff(scalar):
    try: 
        scalar = float(scalar)
        if scalar == int(scalar):
            scalar = int(scalar)
    except:
        pass
    return scalar


def series_type_sniff(series):
    try: 
        series = series.astype(float)
        if all(series == series.astype(int)):
            series = series.astype(int)
    except:
        pass
    return series


def results_wrapper(data, 
                    print_notes=True,
                    set_index=None,
                    heading=None):

    def ga_clean(varname): 
        return varname.replace('ga:', '')

    def add_df_heading(df, heading):
        return pd.concat([df], axis=1, keys=[heading])

    if print_notes:
        query = data['id']
        print(query)

    col_heads = [ga_clean(c.get('name')) for c in data['columnHeaders']]
    data_rows = data.get('rows')

    if not data_rows:
        print("No results")
        return None

    assert len(col_heads) == len(data_rows[0])
        
    data_row_dicts = [{k:v for (k, v) in zip(col_heads, row)}
                      for row in data_rows]

    df = pd.DataFrame(data_row_dicts)    

    for c in df.columns:
        df[c] = series_type_sniff(df[c])

    if print_notes:
        warning = u"Result {} contain sampled data.".format(
            {True: u"DOES", False: u"does not"}          
            [data['containsSampledData']])
        print(warning)
    
    if set_index:
        df.set_index(set_index, inplace=True)

    if heading:
        return add_df_heading(df, heading)
    else:
        return df
   

class ga_context:
    ''' 
    initialize a GA service instance with a view_id and
    a date range, to provide a shorthand for multiple related queries.

    usage:
        c = ga_context(view_id='ga:11111111', ('2015-01-01','2015-03-31'), label='Q1 2015')

        df1 = c.get() # default values: returns a dataframe with one number, total pageviews

        df2 = c.get(dimensions='ga:pageTitle') # titles by pageview count

        df3 = c.get(metrics='ga:pageviews', # default
                    sort='-ga:pageviews',   # default
                    filters='ga:pagePath=@site.com/folder,' #default=None
                            'ga:pagePath=@site.com/etc',
                    dimensions='ga:pageTitle',              #default=None
                    samplingLevel='HIGHER_PRECISION',
                    )
    '''
    # Default kwargs in a context object are set as each query is made, which 
    # can produce unexpected results - that functionality should be removed.
    # (but for safety the full query URL is printed, so default values can be read off.)

    def __init__(self, view_id, date_range=None, start_date=None, end_date=None, label=None):
        if date_range:
            start_date = date_range[0]
            end_date = date_range[1]

        if not start_date and end_date:
            raise ValueError('date range or start/end dates must be specified')

        self.view_id = view_id
        self.start_date = start_date
        self.end_date = end_date
        self.service = initialize_service()
        self.label = label
        self.default_query = dict(metrics='ga:pageviews',
                                  filters=None,  
                                  dimensions=None,
                                  sort='-ga:pageviews',
                                  max_results=1000,
                                  samplingLevel='HIGHER_PRECISION')

    def update_default_query(self, **update_items):
        self.default_query.update(update_items)

    def description(self):
        return (u'{l} ({s} to {e})'.format(l=self.label, 
                                           s=self.start_date, 
                                           e=self.end_date))

    def get(self, raw=False, show_heading=False, **kwargs):
        kw_default = self.default_query
        kw_default.update(kwargs)
        get_obj = self.service.data().ga().get(
            ids=self.view_id, 
            start_date=self.start_date, 
            end_date=self.end_date, 
            #metrics='ga:pageviews',
            #sort='-ga:pageviews',
            #filters=filters,
            #dimensions=dimensions,
            #samplingLevel='HIGHER_PRECISION',
            **kw_default
            )
        if self.label:
            print(self.description())
        result = get_obj.execute()
        if raw:
            return result
        if show_heading:
            df_out = results_wrapper(result, heading=self.description())
        else:
            df_out = results_wrapper(result)
        return df_out


    def get_one(self, **kwargs):
        ''' 
        returns a scalar instead of a dataframe, and ensures that only one 
        value was returned by the API.
        '''
        df = self.get(**kwargs)
        if df is None:
            print('(no results)')
            return None
        if len(df.index) == 1 and len(df.columns) == 1:
            return df.iloc[0,0]
        else:
            raise ValueError(("result should contain just one value\n\n",
                              str(df)))




# Declare constants and set configuration values

# The file with the OAuth 2.0 Client details for authentication and authorization.
from os import path
CLIENT_SECRETS = path.join(path.dirname(__file__), 'csec.json')
print('OAuth 2.0 Client auth secrets file: ', CLIENT_SECRETS)

# A file to store the access token
TOKEN_FILE_NAME = path.join(path.dirname(__file__), 'analytics.dat')

# The Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/analytics.readonly',
    message='client secrets JSON is missing: %s' % CLIENT_SECRETS)


def prepare_credentials():
    # Retrieve existing credendials
    storage = Storage(TOKEN_FILE_NAME)
    credentials = storage.get()

    # If existing credentials are invalid and Run Auth flow
    # the run method will store any new credentials
    if credentials is None or credentials.invalid:
        credentials = run(FLOW, storage) 
        #run Auth Flow and store credentials
    return credentials


def initialize_service():
    # 1. Create an http object
    http = httplib2.Http()

    # 2. Authorize the http object
    # In this tutorial we first try to retrieve stored credentials. If
    # none are found then run the Auth Flow. This is handled by the
    # prepare_credentials() function defined earlier in the tutorial
    credentials = prepare_credentials()
    http = credentials.authorize(http)  # authorize the http object

    # 3. Build the Analytics Service Object with the authorized http object
    return build('analytics', 'v3', http=http)



#-----------------------------------------------------------
# additional convenience functions


def context_comparison(context_list, query_dict, 
                       set_index=None, collapse_column_labels=False):
    
    dfs = {c.label: c.get(**query_dict)
          for c in context_list}
    if set_index:
        for k in dfs.keys():
            dfs[k] = dfs[k].set_index(set_index)
            
    outdf = pd.concat(dfs, axis=1)
    if collapse_column_labels:
        outdf.columns = ['{}: {}'.format(a, b)
                         for (a, b) in outdf.columns]    
    return outdf


def query_comparison(query_dict_dict, context, 
                     set_index=None, collapse_column_labels=False):
    
    dfs = {qkey: context.get(**query)
          for qkey, query in query_dict_dict.items()}    
    if set_index:
        for k in dfs.keys():
            dfs[k] = dfs[k].set_index(set_index)
            
    outdf = pd.concat(dfs, axis=1)
    print(outdf.columns)
    if collapse_column_labels:
        outdf.columns = ['{}: {}'.format(a, b)
                         for (a, b) in outdf.columns] 
    return outdf