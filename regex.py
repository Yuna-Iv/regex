"""FSA"""
from __future__ import annotations
from abc import ABC, abstractmethod

class State(ABC):
    """
    state
    """
    @abstractmethod
    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")

class StartState(State):
    """
    start state.
    """
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class TerminationState(State):
    """
    final state.
    """
    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym


class StarState(State):
    """
    state for *
    """
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class PlusState(State):
    """
    state for +
    """
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class RegexFSM:
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()

        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        tail_states: list[State] = [self.curr_state]
        parents_of_tmp: list[State] = []

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, parents_of_tmp, tmp_next_state)

            if char == "*":
                tail_states = [tmp_next_state] + parents_of_tmp
            elif char == "+":
                tail_states = [prev_state, tmp_next_state]
            else:
                for state in tail_states:
                    state.next_states.append(tmp_next_state)
                parents_of_tmp = tail_states.copy()
                prev_state = tmp_next_state
                tail_states = [tmp_next_state]

        term = TerminationState()
        for state in tail_states:
            state.next_states.append(term)

    def __init_next_state(
        self, next_token: str, prev_state: list[State], tmp_next_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()

            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
                for parent in prev_state:
                    parent.next_states = [s for s in parent.next_states if s is not tmp_next_state]
                    parent.next_states.append(new_state)
                new_state.next_states.append(new_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
                tmp_next_state.next_states.append(new_state)
                new_state.next_states.append(new_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, string: str):
        def dfs_match(state: State, index: int) -> bool:
            if isinstance(state, TerminationState):
                return index == len(string)
            if index > len(string):
                return False
            for next_state in state.next_states:
                if isinstance(next_state, TerminationState):
                    if dfs_match(next_state, index):
                        return True
                elif index < len(string) and next_state.check_self(string[index]):
                    if dfs_match(next_state, index + 1):
                        return True
            return False

        return dfs_match(self.curr_state, 0)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))     # True
    print(regex_compiled.check_string("4uhi"))           # True
    print(regex_compiled.check_string("meow"))           # False
    print(regex_compiled.check_string("4hi"))            # False
    print(regex_compiled.check_string("a4xhi"))          # True
    print(regex_compiled.check_string("aaaa4xyz123hi"))  # True
    print(regex_compiled.check_string("b4xhi"))          # False
    print(regex_compiled.check_string("aaaxhi"))         # False
    print(regex_compiled.check_string("4xhii"))          # False
    print(regex_compiled.check_string("4xh"))            # False
    print(regex_compiled.check_string(""))               # False
