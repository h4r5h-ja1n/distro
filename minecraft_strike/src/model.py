import sys
import math
import random
import time
import threading
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse
import minecraft_strike.src.variable as var_
from collections import deque
import minecraft_strike.src.arr as arr_
#import tmp8 as t_
from minecraft_strike.src.hardcode2 import structures as bui
class Model(object):

    def __init__(self):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load("assets/PKYMK.png").get_texture())
        #images for player
        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}
        # maps the mormalized position to the real position
        self.tmp = {}
        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self.power_time=0

        self._initialize()

    def features(self):
        pass
#        self.add_block((2, -1, 2), var_.COIN, immediate=False)
#        var_.FEATURES[(2, -1, 2)] = "fly"
#        self.add_block((2, 20, 3), var_.COIN, immediate=False)
#        var_.FEATURES[(2, 20, 3)] = "fly"
#        self.add_block((24, -1, 4), var_.COIN, immediate=False)
#        var_.FEATURES[(24, -1, 4)] = "fly"
#        self.add_block((23, -1, 2), var_.COIN, immediate=False)
#        var_.FEATURES[(23, -1, 2)] = "fly"
      #  self.tt((4,4,4))
    def tt(self, position):
        self._shown[position] = self.batch.add(4, GL_QUADS, self.group1,
            ('v3f/static', var_.square_vertices(position, 1)),
            ('t2f/static', [0,0,1,0,1,1,0,1]))



    def _initialize(self):
        """ Initialize the world by placing all the blocks.

        """
  #      self.add_block((0, 20 - 2, 0), var_.GRASS, immediate=False)
        self.features()
        n = 80  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in range(-n, n + 1, s):
            for z in range(-n, n + 1, s):
                # create a layer var_.STONE an var_.GRASS everywhere
                t=[var_.GRASS1, var_.GRASS2]
                V= random.randint(0, 1)
                if (-81<x<-50 or 50<x<81) and (-81<z<-50 or 50<z<81):
                    self.add_block((x, y - 2, z), t[V], immediate=False)
                else:
                    self.add_block((x, y - 2, z), var_.NOR, immediate=False)
                self.add_block((x, y - 3, z), var_.STONE, immediate=False)
                if (-50<=x<=-40 or 40<=x<=50 or -25<x<-13 or 13<x<25) or(-50<=z<=-40 or 40<=z<=50 or -25<z<-13 or 13<z<25):
                    self.add_block((x,-2,z),var_.ROAD,immediate=False)
                if (not(-50<=x<=-40 or 40<=x<=50 or -25<x<-13 or 13<x<25) and (z==-48 or z==-42 or z==42 or z==48 or z==23 or z==15 or z==-23 or z==-15)) :
                    self.add_block((x,-1,z),var_.FLOW1,immediate=False)
                if ( not(-50<=z<=-40 or 40<=z<=50 or -25<z<-13 or 13<z<25)and (x==-48 or x==-42 or x==42 or x==48 or x==23 or x==15 or x==-23 or x==-15)):
                    self.add_block((x,-1,z),var_.FLOW2,immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in   range(-2, 30):
                        self.add_block((x, y + dy, z), var_.STONE, immediate=False)
#        t=[var_.RSTONE,var_.ALGAE,var_.SNOW, var_.MARBLE]
#        for d,e in zip(arr_.arr_h, arr_.arr_ht):
#                self.add_block(d,t[e+1], immediate=False)
#        t=[var_.GRASS, var_.SAND, var_.BRICK]
#        for d,e in zip(arr_.arr_h2, arr_.arr_h2t):
#                self.add_block(d,t[e+1], immediate=False)
#
#        for i,j in t_.arra.iteritems():
#            self.add_block(i, var_.FLOOR1, immediate=False)
        #contoller for the map
        bui_ =bui(1)
        assign=1
        pointer=0
        if assign==0:
            arr=[]
        else:
            arr = [2, 2, 3, 3, 3, 2, 2, 3, 2, 3, 3, 3, 3, 3, 2, 3, 2, 2, 3, 3]
        tmp = [-73,-59,-32,32,59,73]
        for i in tmp:
            for j in tmp:
                if not ((abs(i)==73 or abs(i)==59 )and(abs(j)==73 or abs(j)==59 ) ):
                    t=random.randint(2,3)
                    if assign ==0:
                        arr.append(t)
                    else:
                        t=arr[pointer]
                        pointer+=1
                    bui_.building(self,i,-1,j,t*6,6,6,t)
        tmp = [-65,65]
        for i in tmp:
            bui_.building(self,0,-1,i,10,13,13)
            bui_.building(self,i,-1,0,10,13,13)
        tmp = [-32,32]
        for i in tmp:
            bui_.building(self,0,-1,i,5,7,12,1)
            bui_.building(self,i,-1,0,5,12,7,1)
        bui_.tower(self,0,-1,0,15,7,7,1)
        print(arr)
        print(bui_.arr)
        print(bui_.arr1)


    def hit_test(self, position, vector, max_distance=20):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(max_distance * m):
            key = var_.normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in var_.FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True,tmp=0,object_=None):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `var_.tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if tmp != 0:
            object_.Send({"action":"add","player":object_.mainid,"position":position,"texture":texture})
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(var_.sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True,tmp=0,object_=None):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
       # print(position)
        data = -1
        if position in self.tmp:
            c=position
            data = self.tmp[position]
            object_.player_arr[data[1]].health-=1
            if object_.player_arr[data[1]].health == 0:
                object_.player_arr[data[1]]._shown1.pop(data[0]).delete()
                del self.world[c]
                del self.tmp[c]
            data=data[1]
        else:
            del self.world[position]
            self.sectors[var_.sectorize(position)].remove(position)
            if immediate:
                if position in self.shown:
                    self.hide_block(position)
                self.check_neighbors(position)
        if tmp != 0:
            print({"action":"rem","player":object_.mainid,"position":position,"texture":data})
            object_.Send({"action":"rem","player":object_.mainid,"position":position,"texture":data})

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in var_.FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `var_.tex_coords()` to
            generate.

        """
        x, y, z = position
        vertex_data = var_.cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in range(-pad, pad + 1):
            for dy in [0]:  # range(-pad, pad + 1):
                for dz in range(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / var_.TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()
