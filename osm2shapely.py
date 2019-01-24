#-*- coding: utf-8 -*-
#
# Code fourni par JB : http://osm.org/user/JBacc1 ou @RandoCarto (https://twitter.com/RandoCarto) sous licence GPL v3 ou suivantes

from osmdata import *
import shapely.geometry
import pyproj

WEBMERCATOR=pyproj.Proj(init="EPSG:3857")


def osmNode2shapelyPoint(p):
	x,y=WEBMERCATOR(p.location.x,p.location.y)
	return shapely.geometry.Point(x,y)
def osmPoint2shapelyPoint(p):
	x,y=WEBMERCATOR(p.x,p.y)
	return shapely.geometry.Point(x,y)
def osmWay2shapelyLinestring(way,osm):
	points=[]
	for node_id in way.nodes:
		node=osm.nodes[node_id]
		points.append(WEBMERCATOR(node.location.x,node.location.y))
	return shapely.geometry.LineString(points)
def osmWay2shapelyPolygon(way,osm):
	points=[]
	for node_id in way.nodes:
		node=osm.nodes[node_id]
		points.append(WEBMERCATOR(node.location.x,node.location.y))
	if points.pop()!=points[0]: raise ValueError("Way non ferme lors de la creation d'un polygon. way_id="+str(way.id))
	return shapely.geometry.Polygon(points)
def osmMultipolygonLargestOuter2shapelyPolygon(rel,osm):
	"""Experimental. Ne fonctionne qu'avec des membres outer fermés."""
	if not rel.has_tag("type","multipolygon"): 
		print("Avertissement : la relation "+str(rel.id)+"n'est pas de type multipolygone, mais tente d'être traitée comme tel")
	max_area=-1
	member_id=0
	for member in rel.members:
		if member.ref_type=="way" and (member.role=="outer" or member.role==""):
			if osm.way(member.ref_id).is_closed:
				pol=osmWay2shapelyPolygon(osm.way(member.ref_id),osm)
				if pol.area>max_area: member_id=member.ref_id
	
	if member_id==0:
		pol=shapely.geometry.Polygon() #empty polygon
	else:
		pol=osmWay2shapelyPolygon(osm.way(member_id),osm)
	return pol


def shapelyPoint2osm_add_node(p,osm,tags=[]):
	"""returns node_id"""
	point_xy=WEBMERCATOR(p.x,p.y,inverse=True)
	new_node=OsmNode(osm.make_new_id(),point_xy[0],point_xy[1],tags,"modify","","","","","","")
	osm.add_node(new_node)
	return new_node.id
def shapelyPolygon2osm_add_way(p,osm,tags=[],points_tags=[]):
	"""returns way_id. tags to way, points_tags to points added. Reuse of existing points not yet implemented."""
	point_list=[]
	for point in list(p.exterior.coords)[:-1]: #premier point répété dans la liste
		point_list.append(shapelyPoint2osm_add_node(shapely.geometry.Point(point),osm,points_tags))
	point_list.append(point_list[0])
	new_way=OsmWay(osm.make_new_id(),point_list,tags,"modify")
	osm.add_way(new_way)
	return new_way.id

