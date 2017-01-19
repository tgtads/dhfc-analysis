import scrapy
import re
import datetime
from pitchero_dhfc.items import SportsEventItem, CompetitorItem, FormationItem, SubEventItem, AthleteItem


# dhfc sub-teams
# team_name = ["First XI", "Dulwich Hamlet Under 18s", "Dulwich Hamlet Under 16s"]
# team_number = [56196, 72744, 72745]

today = datetime.date.today()

class Main(scrapy.Spider):
    name = "mainscraper"
    allowed_domains = ["www.pitchero.com"]
    start_urls = [today.strftime("http://www.pitchero.com/clubs/dulwichhamlet/calendar/%Y-%m")]

    def parse(self, response):
        # spider the calendar

        # follow all urls that contain 'calendar/20' (this century)
        for href in response.xpath("//a/@href[contains(., '/calendar/20')]"):
            calUrl = href.extract()
            # use string extraction to find date
            urlmonth = int(calUrl[-7:-3]+calUrl[-2:])
            # only follow links to months prior to this one
            if (urlmonth < int(today.strftime("%Y%m"))):
                yield scrapy.Request(url=response.urljoin(calUrl),
                                     callback=self.parse)

        # follow all links to all first XI match-centres in the page.
        # this includes future events in the current month
        for href in response.xpath("//a/@href[contains(., " +
                                   "'/teams/56196/match-centre')]"):
            eventUrl = href.extract()
            yield scrapy.Request(url=response.urljoin(eventUrl),
                                 callback=self.parse_match_centre)


    def parse_match_centre(self, response):

        sportsEvent = SportsEventItem()

        # get url for match UID

        eventUid = re.search(r"[-0-9]*$", response.url).group(0)

        sportsEvent['eUid'] = eventUid

        sportsEvent['startDateTime'] = response.xpath("//span[@itemprop='startDate']/@content").extract_first()
        sportsEvent['homeTeam'] = response.xpath("//span[@itemprop='homeTeam']/meta/@content").extract_first().encode('utf-8')
        sportsEvent['awayTeam'] = response.xpath("//span[@itemprop='awayTeam']/meta/@content").extract_first().encode('utf-8')
        sportsEvent['location'] = response.xpath("//span[@itemprop='location']/meta/@content").extract_first()
        sportsEvent['latitude'] = response.xpath("//span[@itemprop='geo']/meta[@itemprop='latitude']/@content").extract_first()
        sportsEvent['longitude'] = response.xpath("//span[@itemprop='geo']/meta[@itemprop='longitude']/@content").extract_first()
        sportsEvent['homeScore'] = response.xpath("//span[@class='match-report-tile__score u-text-shadow js-home-score ']/text()").extract_first().strip()
        sportsEvent['awayScore'] = response.xpath("//span[@class='match-report-tile__score u-text-shadow away_team js-away-score ']/text()").extract_first().strip()
        sportsEvent['duration'] = response.xpath("//div[@id='as-it-happened']//ul/@data-duration").extract_first()
        blurb = "".join(response.xpath("//span[@class='u-block u-muted u-text-center u-space-bottom--small' and position()=1]//text()").extract())
        sportsEvent['competition'] = re.sub(r"^.*(:[0-9]{2}|TBC)\ -\ ", "", blurb).encode('utf-8')
        sportsEvent['nAttendees'] = re.sub(",", "", re.sub("Attendance\ ", "", "".join(response.xpath("//span[@class='u-block u-muted u-text-center u-space-bottom--small' and position()=2]/text()").extract())))
        yield sportsEvent

        # summary = response.xpath("//div[@class='o-layout u-muted']")

        # match report - discarded as no intention of analysing at this stage
        # response.xpath("//div[@id='match-report']")

        # the <p> part of the match report also gives detailed like-for-like sub info
        # regex may be needed, but preferred if innerhtml is preserved
        # response.xpath("//div[@id='match-report']//em")


        # add team selection to competitors.csv


        # obtaining competitors
        


        # scrape for the competing players
        # and their game-specific attributes
        for teamnode in response.xpath("//div[@class='layout__item u-lap-and-up-one-third']"):
            if teamnode.xpath("ul[@class='o-list-bare']"):
                team = teamnode.xpath("strong/text()").extract_first().encode('utf-8')
                for item in teamnode.xpath("ul[@class='o-list-bare']/li"):
                    if item.xpath("a"):
                        ns = item.xpath("a/text()").extract_first().strip().encode('utf-8')
                    else:
                        ns = item.xpath("text()").extract_first().strip().encode('utf-8')
                    if re.match("[0-9]{1,2}\. ", ns):
                        competitor = CompetitorItem()
                        (competitor['shirtNumber'], competitor['name']) = re.split("\. ", ns)
                        competitor['eUid'] = eventUid
                        competitor['affiliation'] = team
                        url = item.xpath("a/@href").extract_first()
                        if url:
                            idm = re.match(r".*-([0-9]*)", url)
                            competitor['cUid'] = idm.group(1)
                        else:
                            competitor['cUid'] = ""
                        yield competitor


        # team selection gives formation and positional information
        # this can be merged with competitor using eUid and cUid
        fop = response.xpath("//div[@id='team-selection']/div[@class='o-layout']/div[@class='layout__item u-lap-and-up-two-thirds u-palm-hide']/div[@class='c-selection']/div[@class='c-field-of-play u-relative']")
        if len(fop) > 0:
            for item in fop.xpath("div"):
                formation = FormationItem()
                s = item.xpath("@data-href").extract_first()
                if s:
                    formation['cUid'] = re.match(r".*-([0-9]*)", s).group(1)
                else:
                    formation['cUid'] = ""
                formation['eUid'] = eventUid
                pzm = re.match(r"left:(.*)%;bottom:(.*)%;", item.xpath("@style").extract_first())
                (formation['lpos'], formation['bpos']) = pzm.group(1, 2)
                yield formation     

        # TODO: IF THE THERE IS NO URL or DATA-HREF IN IDM, WE MUST LOOK IN THE CONTENT FOR THE NAME. OR FIX IT MANUALLY.         

        # as it happened gives competitor-action information
        for li in response.xpath("//div[@id='as-it-happened']/ul/li"):
            if li.xpath("@data-minute"):
                subEvent = SubEventItem()
                subEvent['eUid'] = eventUid
                subEvent['minute'] = li.xpath("@data-minute").extract_first()
                subEvent['competitorName'] = li.xpath("div/small[position()=1]/text()").extract_first().encode('utf-8')
                subEvent['description'] = li.xpath("div/small[position()=2]/text()").extract_first().encode('utf-8')
                yield subEvent

        # as the site is spotty when including player urls, scrape the whole page for player urls
        # scrapy avoids duplication
        # go to any player page found, and parse it
        for playerUrl in response.xpath("//a/@href[contains(., '/player/')]").extract():
            yield scrapy.Request(url=response.urljoin(playerUrl),
                                 callback=self.parse_player_page)


    def parse_player_page(self, response):
        # extract player id from the url too. This is specific to the team, so 
        # a single player on 2 different teams will have 2 cUids
        cUid = re.match(r".*-([0-9]*)(/[0-9]*)?$", response.url).group(1)
        
        name = response.xpath("//div[@class='layout__item u-lap-and-up-one-half']/h2/text()").extract_first().encode('utf-8')
        athlete = AthleteItem()
        
        athlete['cUid'] = cUid
        athlete['name'] = name
        athlete['position'] = response.xpath("//div[@class='layout__item u-lap-and-up-one-half']/span[@class='u-muted u-text--delta u-block u-space-bottom']/text()").extract_first()
        # bio = ''.join(response.xpath("//div[@class='js-shorten']/strong/../text()").extract())
        # bio = re.sub("\ {2,}", "", bio)
        # athlete['description'] = re.sub("\n", "", bio)
        yield athlete

        # find all events for the season: 
        # some where they are competitors.. but no match report exists
        # some of these won't be found, some will
        # we will need to remove dupes later
        for eventUrl in response.xpath("//div[@class='layout__item u-two-twelfths u-palm-hide u-text-ellipsis']/a/@href").extract():
            competitor = CompetitorItem()
            competitor['eUid'] = re.search(r"[-0-9]*$", eventUrl).group(0)
            competitor['cUid'] = cUid 
            competitor['name'] = name
            competitor['affiliation'] = "Dulwich Hamlet" # implicit to this run
            competitor['shirtNumber'] = "" # no match report
            yield competitor

        # find other seasons and parse them as player pages (dupes ignored)    
        for seasonUrl in response.xpath("//div[@class='dropdown__body dropdown__body--right u-bg-white o-box box--tiny u-border u-drop-shadow']/ul/li/a/@href[contains(., '/player/')]").extract():
            yield scrapy.Request(url=response.urljoin(seasonUrl),
                                 callback=self.parse_player_page)


        # due to 1) the scarcity of images on pitchero
        # and 2) the small number of images
        # images pipeline might not be implemented
        # img = ImagesItem()
        # imgloc = response.xpath("//div[@class='layout__item u-lap-and-up-one-half u-palm-space-bottom']") # contains an image, which has href attributes of
        # imghref = imgloc.xpath("img/@src[contains(., '&w=800&h=800&t=square&q=40')]").extract()
        # The filename should be saved with the parent page url. use re. ".+/" to strip the filename
        # (.+)/([^/]+) # \1 \2 dir and fn