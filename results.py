#!/usr/bin/python
import sqlite3
import json
import os.path

class Results:
    def __init__(self, filename):
        if not os.path.isfile(filename):
            self.db = sqlite3.connect(filename)
            cursor=self.db.cursor()
            cursor.execute('CREATE TABLE "results" ("Id" INTEGER PRIMARY KEY, "Density" REAL, "Experiment" INTEGER, "Order" INTEGER, "Position" INTEGER, "Time" REAL)')
            self.db.commit()
            cursor.close()
        else:
            self.db = sqlite3.connect(filename)
            
    def add(self, data, density, experiment):
        cursor=self.db.cursor()
        for order, result in enumerate(data):
            for position, time in enumerate(result):
                cursor.execute('INSERT INTO "results" VALUES(null, ?, ?, ?, ?, ?)', (density, experiment, order, position, time))
        self.db.commit()
        cursor.close()
            
    def getExperimentCount(self, density):
        cursor=self.db.cursor()
        cursor.execute('SELECT COUNT(DISTINCT "Experiment") FROM "results" WHERE "Density"=?', (density,))
        count = cursor.fetchone()
        cursor.close()
        return count[0]
    
    def getDensities(self):
        cursor=self.db.cursor()
        cursor.execute('SELECT DISTINCT "Density" FROM "results"')
        densities = [i[0] for i in cursor.fetchall()]
        cursor.close()
        return densities

    def getPositions(self):
        cursor=self.db.cursor()
        cursor.execute('SELECT DISTINCT "Position" FROM "results"')
        positions = [i[0] for i in cursor.fetchall()]
        cursor.close()
        return positions
        
    def getData(self, density, position):
        cursor=self.db.cursor()
        cursor.execute('SELECT "Time" FROM "results" WHERE "Density"=? AND "Position"=?', (density, position))
        data = [i[0] for i in cursor.fetchall()]
        cursor.close()
        return data
