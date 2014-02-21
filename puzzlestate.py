#! /usr/bin/env python

from collections import defaultdict

class PuzzleState:
    W = 6
    H = 5
    MAP_SIZE = W * H
    DELETE_UNIT = 3
    U = -W
    D = -U
    R = 1
    L = -R

    def __init__(self, state_list, initial_position, history = []):
        self.state = state_list[:]
        self.position = initial_position
        self.history = history[:]
        self.extract_deletes = self.cache_func_factory(self._extract_deletes)
        self.score = self.cache_func_factory(self._score)
        self.search_score = self.cache_func_factory(self._search_score)
        self.connection_score = self.cache_func_factory(self._connection_score)

    def x(self):
        return self.position / PuzzleState.W

    def y(self):
        return self.position % PuzzleState.W

    def cache_func_factory(self, method):
        name = method.__name__
        cache_name = '_' + name
        def cache_func():
            if hasattr(self, cache_name): return getattr(self, cache_name)
            value = method()
            setattr(self, cache_name, value)
            return value
        return cache_func

    def swap(self, distance):
        self.state[self.position] ^= self.state[self.position + distance]
        self.state[self.position + distance] ^= self.state[self.position]
        self.state[self.position] ^= self.state[self.position + distance]

    def adjacent_positions(self, position):
        x = position / PuzzleState.W
        y = position % PuzzleState.W
        if x + 1 < PuzzleState.H: yield position + PuzzleState.D
        if x - 1 >= 0: yield position + PuzzleState.U
        if y + 1 < PuzzleState.W: yield position + PuzzleState.R
        if y - 1 >= 0: yield position + PuzzleState.L

    def _extract_deletes(self):
        delete_drop = set()
        for start in xrange(PuzzleState.MAP_SIZE):
            sx = start / PuzzleState.W
            sy = start % PuzzleState.W
            vertical = range(start, PuzzleState.MAP_SIZE, PuzzleState.D)[:PuzzleState.DELETE_UNIT]
            horizontal = range(start, PuzzleState.MAP_SIZE, PuzzleState.R)[:PuzzleState.DELETE_UNIT]
            if len(vertical) == PuzzleState.DELETE_UNIT:
                if all(self.state[p] == self.state[start] for p in vertical):
                    delete_drop |= set(vertical)
            if len(horizontal) == PuzzleState.DELETE_UNIT:
                if all(self.state[p] == self.state[start] for p in horizontal):
                    delete_drop |= set(horizontal)
        deletes = defaultdict(list)
        used_drop = set()
        for p in delete_drop:
            if p in used_drop: continue
            color = self.state[p]
            delete_set = []
            stack = [p]
            while stack:
                pos = stack.pop()
                delete_set.append(pos)
                used_drop.add(pos)
                for npos in self.adjacent_positions(pos):
                    if npos in delete_drop and self.state[npos] == color and npos not in used_drop:
                        stack.append(npos)
            deletes[color].append(delete_set)
        return deletes

    def _score(self):
        score = 0
        for deletes in self.extract_deletes().values():
            score += len(deletes)
        return score

    def _connection_score(self):
        score = 0
        for x in xrange(PuzzleState.H):
            for y in xrange(PuzzleState.W):
                p = x * PuzzleState.W + y
                if x + 1 < PuzzleState.H:
                    if self.state[p] == self.state[p + PuzzleState.D]: score += 1
                if y + 1 < PuzzleState.W:
                    if self.state[p] == self.state[p + PuzzleState.R]: score += 1
        return score

    def _search_score(self):
        return self.score() + 0.1 * self.connection_score() - 0.01 * len(self.history)

    def is_backstep(self, direction):
        return len(self.history) > 0 and self.history[-1] == -direction

    def next_state(self, direction):
            state = PuzzleState(self.state, self.position + direction, self.history + [direction])
            state.swap(-direction)
            return state

    def next_states(self):
        if self.x() - 1 >= 0 and not self.is_backstep(PuzzleState.U): #up
            yield self.next_state(PuzzleState.U)
        if self.x() + 1 < PuzzleState.H and not self.is_backstep(PuzzleState.D): #down
            yield self.next_state(PuzzleState.D)
        if self.y() - 1 >= 0 and not self.is_backstep(PuzzleState.L): #left
            yield self.next_state(PuzzleState.L)
        if self.y() + 1 < PuzzleState.W and not self.is_backstep(PuzzleState.R): #right
            yield self.next_state(PuzzleState.R)

    def __repr__(self):
        return "State<position = (%d, %d), steps = %d, score = %f, search_score = %f>" % (self.x(), self.y(), len(self.history), self.score(), self.search_score())

    __str__ = __repr__

    def debug_print(self):
        print self
        for x in xrange(PuzzleState.H):
            for y in xrange(PuzzleState.W):
                p = x * PuzzleState.W + y
                if x == self.x() and y == self.y():
                    print "[%d]" % self.state[p],
                else:
                    print " %d " % self.state[p],
            print
                    
if __name__ == "__main__":
    import random
    init_state = [random.randrange(5) for x in xrange(30)]
    beam = [PuzzleState(init_state, p) for p in xrange(30)]
    beam_size = 300

    beam[0].debug_print()

    for loop_num in xrange(20):
        print "Loop", loop_num
        # print "Best Solution:"
        # beam[0].debug_print()
        next_states = sum([list(state.next_states()) for state in beam], [])
        next_states += beam
        next_states.sort(key = lambda s: s.search_score(), reverse = True)
        beam = next_states[:beam_size]
    
    beam[0].debug_print()
