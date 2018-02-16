# pavement_condition_to_street.py
# This script to use to join Champaign city's pavement condition to CUUATS
# street centerline

from cuuats.datamodel import feature_class_factory as factory
from cuuats.datamodel import D
import os
import arcpy
import config

APPROACH_PATH = os.path.join(SDE_DB, APPROACH_NAME)
Approach = factory(APPROACH_PATH, follow_relationships=True)
Segment = Approach.related_classes[SEGMENT_NAME]
Intersection = Approach.related_classes[INTERSECTION_NAME]
Table = factory(COND_PATH)

streetintersectionapproach = "pcd.pcdqc.streetintersectionapproach_set"

def replace_abbr(str):
    str = str.replace("DRIVE", "DR")
    str = str.replace("STREET", "ST")
    str = str.replace("AVENUE", "AVE")
    return str

def convert_to_upper(str):
    if str is not None:
        str = str.upper()
    return str

def remove_direction(str):
    if str is not None:
        replacement_list = ["W ", "S ", "E ", "W "]
        for r in replacement_list:
            if str[0:2] == r:
                str = str[2: len(str)]
        return str



def main():
    count = 0
    match = 0
    match_list = []
    # loop through all cuuats segment
    for segment in Segment.objects.filter(InUrbanizedArea=D("Yes")):
        intersecting_street = {}
        # loop through all the approaches and get intersecting street
        for approach in getattr(segment, streetintersectionapproach):
            if approach.LegDir == "W":
                intersecting_street[convert_to_upper(approach.IntersectionID.NSRoadway)] = "E"
            elif approach.LegDir == "E":
                intersecting_street[convert_to_upper(approach.IntersectionID.NSRoadway)] = "W"
            elif approach.LegDir == "N":
                intersecting_street[convert_to_upper(approach.IntersectionID.EWRoadway)] = "S"
            elif approach.LegDir == "S":
                intersecting_street[convert_to_upper(approach.IntersectionID.EWRoadway)] = "N"

        # segment.Name
        # segment.SegmentID
        # intersecting_street with direction
        # field_map = ("Branch_Name", "From_", "To", "SegmentID")

        with arcpy.da.UpdateCursor(COND_PATH, field_map) as cursor:
            for row in cursor:
                segment_name = remove_direction(convert_to_upper(segment.Name))
                if row[0] == segment_name:
                    print('match name at least...')
                    if intersecting_street.get(row[1], False) and \
                       intersecting_street.get(row[2], False):
                       print("match: segmentID: {}".format(segment.SegmentID))
                       match_list.append([segment.SegmentID, row[0]])
                       match += 1
                       row[3] = segment.SegmentID
                       cursor.updateRow(row)
        count += 1
        print("count: {}".format(count))
    print(match_list)

if __name__ == "__main__":
    main()
