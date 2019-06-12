import json
import os.path
import logging
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import os, sys, argparse, time, multiprocessing, math, itertools, datetime
from multiprocessing import Queue,Process
from random import randint

try:
    from instagram_private_api import (
        Client, __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, __version__ as client_version)

def get_follower(user_id,limit=1000):
    '''
    return a df of all follower's features of a particular user on Instagram
    '''
    followers = []
    results = api.user_followers(str(user_id),rank_token=rank_token)
    followers.extend(results.get('users', []))
    next_max_id = results.get('next_max_id')
    while next_max_id:
        results = api.user_followers(user_id, max_id=next_max_id,rank_token=rank_token)
        followers.extend(results.get('users', []))
        if len(followers) >= limit:   # get only first 600 or so
            break
        next_max_id = results.get('next_max_id')
    #remove columns with info not necessary to find user
    return (pd.DataFrame(followers))[['pk','username','full_name']].drop_duplicates()

def get_following(user_id,limit=1000):
    '''
    return a df of all following's features of a particular user on Instagram
    '''
    following = []
    results = api.user_following(str(user_id),rank_token=rank_token)
    following.extend(results.get('users', []))
    next_max_id = results.get('next_max_id')
    while next_max_id:
        results = api.user_following(user_id, max_id=next_max_id,rank_token=rank_token)
        following.extend(results.get('users', []))
        if len(followers) >= limit:   # get only first 600 or so
            break
        next_max_id = results.get('next_max_id')
    #remove columns with info not necessary to find user
    return (pd.DataFrame(following))[['pk','username','full_name']].drop_duplicates()

def all_follower_following():
    '''
    return dataframe of all follower+following
    '''
    myid = current_user_id()
    following = get_following(myid,limit=100000**2)
    follower = get_follower(myid,limit=100000**2)
    #merge and delete duplicate in case that i have a (follow back)
    return (following.append(follower)).drop_duplicates()

def pending_users():
    '''
    return list of users in pending request of follow
    '''
    list = api.friendships_pending()['suggested_users']['suggestions']
    return [x['user']['pk'] for x in list]

def current_user_id():
    return api.current_user()['user']['pk']

def user_ids_of_a_search(query):
    return pd.DataFrame(api.search_users(query)['users']).pk.unique()

def add_friends(from_who,howmany):
    merge = all_follower_following()
    mypk = merge.pk.unique()
    counter = 0
    user_ids = user_ids_of_a_search(from_who)
    utilspk = []
    for user in user_ids:
        other = get_follower(user,limit=20000)
        otherpk = other.pk.unique()
        temp = list(set(otherpk)-set(mypk)) 
        utilspk.extend( list( set(temp) - set(pending_users()) ) )
        mydata = [json.dumps(int(x)) for x in utilspk]
        while counter < howmany:
            for new_friend in mydata:
                try:
                    api.friendships_create(new_friend)
                    time.sleep(20) #20 seconds is a good compromise (slow down! too fast is not a good idea)
                except Exception as e:
                    print('Request limit, take a break; Instagram is not happy! try after 2-3 hour')
                    return None
                counter += 1
                print('added_friend: ',other[other.pk == int(new_friend)].username.values[0])
                if counter >= howmany:
                    print()
                    print('All Friends added as request')
                    print('quit')
                    return None
                else:
                    pass
                

if __name__ == '__main__':

    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    # python examples/savesettings_logincallback.py -u "yyy" -p "zzz" -settings "test_credentials.json"
    parser = argparse.ArgumentParser(description='Pagination demo')
    parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    parser.add_argument('-s', '--search', dest='search', type=str, required=True)
    parser.add_argument('-n', '--number', dest='number', type=int, required=True)
    parser.add_argument('-debug', '--debug', action='store_true')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    print('Client version: {0!s}'.format(client_version))
    api = Client(args.username, args.password)
    query = args.search
    number = args.number
    
    api = Client(user_name, password)
    rank_token = Client.generate_uuid()
    # ---------- Pagination with max_id ----------
    user_ids = user_ids_of_a_search(query)
    user_added = 0
    myid = current_user_id()

    #add Friends on Instagram
    add_friends(query,number)


