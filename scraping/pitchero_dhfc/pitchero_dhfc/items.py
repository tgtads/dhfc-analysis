# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.item import Item, Field


class SportsEventItem(Item):
    eUid = Field()
    startDateTime = Field()
    homeTeam = Field()
    awayTeam = Field()
    homeScore = Field()
    awayScore = Field()
    location = Field()
    latitude = Field()
    longitude = Field()
    nAttendees = Field()
    duration = Field()
    competition = Field()


class CompetitorItem(Item):
    eUid = Field()
    affiliation = Field()
    cUid = Field()
    shirtNumber = Field()
    name = Field()


class FormationItem(Item):
    cUid = Field()
    eUid = Field()
    lpos = Field()
    bpos = Field()


class SubEventItem(Item):
    eUid = Field()
    minute = Field()
    competitorName = Field()
    description = Field()



class AthleteItem(Item):
    cUid = Field()
    position = Field()
    name = Field()
