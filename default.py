import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,sys,datetime
import BeautifulSoup
import demjson


pluginhandle = int(sys.argv[1])
shownail = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),"icon.png"))
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(pluginhandle, fanart, color2='0xFFFF3300')
TVShowTitle = 'The Colbert Report'

if xbmcplugin.getSetting(pluginhandle,"sort") == '0':
    SORTORDER = 'date'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '1':
    SORTORDER = 'views'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '2':
    SORTORDER = 'rating'

################################ Common
def getURL( url ):
    try:
        print 'The Colbert Report --> getURL :: url = '+url
        txdata = None
        txheaders = {
            'Referer': 'http://www.colbertnation.com/video/',
            'X-Forwarded-For': '12.13.14.15',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)',
            }
        req = urllib2.Request(url, txdata, txheaders)
        #req = urllib2.Request(url)
        #req.addheaders = [('Referer', 'http://www.thedailyshow.com/videos'),
        #                  ('Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)')]
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        error = 'Error code: '+ str(e.code)
        xbmcgui.Dialog().ok(error,error)
        print 'Error code: ', e.code
        return False
    else:
        return link

def addLink(name,url,iconimage='',plot=''):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot, "TVShowTitle":TVShowTitle})
    liz.setProperty('fanart_image',fanart)
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=url,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage=shownail,plot=''):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot, "TVShowTitle":TVShowTitle})
    liz.setProperty('fanart_image',fanart)
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
    return ok


def FULLEPISODES():
    xbmcplugin.setContent(pluginhandle, 'episodes')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
    full = 'http://www.colbertnation.com/full-episodes/'
    allData = getURL(full)

    episodeURLs = re.compile('<a href="(http://www.colbertnation.com/full-episodes/....+?)"').findall(allData) 
    episodeURLSet = set(episodeURLs)

    listings = []
    for episodeURL in episodeURLs:
        if episodeURL in episodeURLSet:
            episodeURLSet.remove(episodeURL)
            episodeData = getURL(episodeURL)

            title=re.compile('<meta property="og:title" content="(.+?)"').search(episodeData)
            thumbnail=re.compile('<meta property="og:image" content="(.+?)"').search(episodeData)
            description=re.compile('<meta property="og:description" content="(.+?)"').search(episodeData)
            airDate=re.compile('<meta itemprop="datePublished" content="(.+?)"').search(episodeData)
            epNumber=re.compile('/season_\d+/(\d+)').search(episodeData)
            link=re.compile('<meta property="og:url" content="(.+?)"').search(episodeData)

            listing = []
            listing.append(title.group(1))
            listing.append(link.group(1))
            listing.append(thumbnail.group(1))
            listing.append(description.group(1))
            listing.append(airDate.group(1))
            listing.append(epNumber.group(1))
            listings.append(listing)

    print listings

    for name, link, thumbnail, plot, date, seasonepisode in listings:
        mode = 10
        season = int(seasonepisode[:-3])
        episode = int(seasonepisode[-3:])
        u=sys.argv[0]+"?url="+urllib.quote_plus(link)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        u += "&season="+urllib.quote_plus(str(season))
        u += "&episode="+urllib.quote_plus(str(episode))
        u += "&premiered="+urllib.quote_plus(date)
        u += "&plot="+urllib.quote_plus(plot)
        u += "&thumbnail="+urllib.quote_plus(thumbnail)
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": BeautifulSoup.BeautifulSoup(name, convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES),
                                                "Plot": BeautifulSoup.BeautifulSoup(plot, convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES),
                                                "Season":season,
                                                "Episode": episode,
                                                "premiered":date,
                                                "TVShowTitle":TVShowTitle})
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image',fanart)
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)

    xbmcplugin.endOfDirectory(pluginhandle)


################################ Play Full Episode

def PLAYFULLEPISODE(name,url):
    data = getURL(url)
    uri = re.compile('mgid:cms:episode:colbertnation.com:\d{6}').findall(data)[0]
    #url = 'http://media.mtvnservices.com/player/config.jhtml?uri='+uri+'&group=entertainment&type=network&site=thedailyshow.com'
    url = 'http://shadow.comedycentral.com/feeds/video_player/mrss/?uri='+uri
    data = getURL(url)
    uris=re.compile('<guid isPermaLink="false">(.+?)</guid>').findall(data)
    stacked_url = 'stack://'
    for uri in uris:
        rtmp = GRAB_RTMP(uri)
        stacked_url += rtmp.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail, path=stacked_url)
    item.setInfo( type="Video", infoLabels={ "Title": name,
                                             "Plot":plot,
                                             "premiered":premiered,
                                             "Season":int(season),
                                             "Episode":int(episode),
                                             "TVShowTitle":TVShowTitle})
    item.setProperty('fanart_image',fanart)
    print stacked_url
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

################################ Grab rtmp        

def GRAB_RTMP(uri):
    furl = None
    swfurl = 'http://media.mtvnservices.com/player/release/?v=4.5.3'
    url = 'http://www.comedycentral.com/global/feeds/entertainment/media/mediaGenEntertainment.jhtml?uri='+uri+'&showTicker=true'
    mp4_url = "http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639+_pxE=/44620/mtvnorigin"
    data = getURL(url)
    widths = re.compile('width="(.+?)"').findall(data)
    heights = re.compile('height="(.+?)"').findall(data)
    bitrates = re.compile('bitrate="(.+?)"').findall(data)
    rtmps = re.compile('<src>rtmp(.+?)</src>').findall(data)
    mpixels = 0
    mbitrate = 0
    lbitrate = 0
    if xbmcplugin.getSetting(pluginhandle,"bitrate") == '0':
        lbitrate = 0
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '1':
        lbitrate = 1720
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '2':
        lbitrate = 1300
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '3':
        lbitrate = 960
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '4':
        lbitrate = 640
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '5':
        lbitrate = 450
    for rtmp in rtmps:
        marker = rtmps.index(rtmp)
        w = int(widths[marker])
        h = int(heights[marker])
        bitrate = int(bitrates[marker])
        if bitrate == 0:
            continue
        elif bitrate > lbitrate and lbitrate <> 0 and furl:
            continue
        elif lbitrate <= bitrate or lbitrate == 0:
            pixels = w * h
            if pixels > mpixels or bitrate > mbitrate:
                mpixels = pixels
                mbitrate = bitrate
                furl = mp4_url + rtmp.split('viacomccstrm')[2]
                #rtmpsplit = rtmp.split('/ondemand')
                #server = rtmpsplit[0]
                #path = rtmpsplit[1].replace('.flv','')
                #if '.mp4' in path:
                #    path = 'mp4:' + path
                #port = ':1935'
                #app = '/ondemand?ovpfv=2.1.4'
                #furl = 'rtmp'+server+port+app+path+" playpath="+path+" swfurl="+swfurl+" swfvfy=true"
    return furl


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]

    return param


params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
    thumbnail=''
try:
    season=int(params["season"])
except:
    season=0
try:
    episode=int(params["episode"])
except:
    episode=0
try:
    premiered=urllib.unquote_plus(params["premiered"])
except:
    premiered=''
try:
    plot=urllib.unquote_plus(params["plot"])
except:
    plot=''

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


if mode==None or url==None or len(url)<1:
    FULLEPISODES()
elif mode==10:
    PLAYFULLEPISODE(name,url)

