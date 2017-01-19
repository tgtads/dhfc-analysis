# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import items


path = "./"



class MainPipeline(object):


    def init_writers(self):

        self.SportsEventCsv = csv.writer(open(path+'SportsEvents.csv', 'wb')) 
        self.SportsEventCsv.writerow(['eUid',
                                      'startDateTime', 
                                      'homeTeam', 
                                      'awayTeam', 
                                      'homeScore', 
                                      'awayScore', 
                                      'location', 
                                      'latitude', 
                                      'longitude', 
                                      'nAttendees', 
                                      'duration', 
                                      'competition'])

        self.CompetitorCsv = csv.writer(open(path+'Competitors.csv', 'wb')) 
        self.CompetitorCsv.writerow(['eUid', 
                                     'affiliation', 
                                     'cUid', 
                                     'shirtNumber', 
                                     'name'])

        self.FormationCsv = csv.writer(open(path+'Formations.csv', 'wb')) 
        self.FormationCsv.writerow(['cUid', 
                                    'eUid', 
                                    'lpos', 
                                    'bpos']) 

        self.SubEventCsv = csv.writer(open(path+'SubEvents.csv', 'wb')) 
        self.SubEventCsv.writerow(['eUid', 
                                   'minute', 
                                   'competitorName', 
                                   'description']) 

        self.AthleteCsv = csv.writer(open(path+'Athletes.csv', 'wb')) 
        self.AthleteCsv.writerow(['cUid', 
                                  'position', 
                                  'name'])


    def open_spider(self, spider):
        self.init_writers()


    def process_item(self, item, spider):

        if isinstance(item, items.SportsEventItem): 
            self.SportsEventCsv.writerow([item['eUid'],
                                          item['startDateTime'], 
                                          item['homeTeam'], 
                                          item['awayTeam'], 
                                          item['homeScore'], 
                                          item['awayScore'], 
                                          item['location'], 
                                          item['latitude'], 
                                          item['longitude'], 
                                          item['nAttendees'], 
                                          item['duration'], 
                                          item['competition']])
            return item

        if isinstance(item, items.CompetitorItem): 
            self.CompetitorCsv.writerow([item['eUid'], 
                                         item['affiliation'], 
                                         item['cUid'], 
                                         item['shirtNumber'], 
                                         item['name']])
            return item

        if isinstance(item, items.FormationItem):
            self.FormationCsv.writerow([item['cUid'],
                                        item['eUid'],
                                        item['lpos'],
                                        item['bpos']])
            return item

        if isinstance(item, items.SubEventItem): 
            self.SubEventCsv.writerow([item['eUid'], 
                                       item['minute'], 
                                       item['competitorName'], 
                                       item['description']]) 
            return item

        if isinstance(item, items.AthleteItem): 
            self.AthleteCsv.writerow([item['cUid'], 
                                      item['position'], 
                                      item['name']])
            return item

