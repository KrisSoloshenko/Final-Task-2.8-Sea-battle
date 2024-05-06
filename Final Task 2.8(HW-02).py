from random import randint


class Dot:
    """Класс точки, атрибуты - значения координат х и у,
        методы: __eq__(реализация сравнения),
        __str__(возврат строки)"""

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"Dot({self.x}, {self.y})"


class Exceptions(Exception):
    """Класс исключений"""
    pass


class BoardOutException(Exceptions):
    """Класс исключения: попадание за пределы поля
    методы: __str__(возврат строки)"""

    def __str__(self):
        return "Вы попали за пределы поля"


class RepeatHitException(Exceptions):
    """Класс исключения: попадание в одну и ту же цель
        методы: __str__(возврат строки)"""

    def __str__(self):
        return "В эту клетку уже стреляли!"


class WrongPositionShipException(Exceptions):
    """Класс исключения: некорректное положение корабля на игровом поле"""
    pass


class Ship:
    """Класс корабля, атрибуты:
        len - длина корабля,
        dot_bow_ship - начальная точка корабля,
        orientation - ориентация корабля на поле 0 - вертикально, 1 - горизонтально,
        dot_hp - жизни корабля, равны длине.
        методы: dots_ship(возвращает список с координатами корабля),
        shooting(проверка на попадание удара в корабль, возвращает bool)"""

    def __init__(self, dot_bow_ship, len, orientation):
        self.len = len
        self.dot_bow_ship = dot_bow_ship
        self.orientation = orientation
        self.dot_hp = len

    @property
    def dots_ship(self):
        dots_list = []

        for i in range(self.len):
            actual_x = self.dot_bow_ship.x
            actual_y = self.dot_bow_ship.y

            if self.orientation == 0:
                actual_x += i
            elif self.orientation == 1:
                actual_y += i

            dots_list.append(Dot(actual_x, actual_y))

        return dots_list

    def shooting(self, shot):
        return shot in self.dots_ship


class GameBoard():
    """Класс игровой доски, атрибуты:
        size - размер игрового поля(строк/столбцов),
        hidden - скрытность поля для видимости игрока,
        count - счетчик потопленных кораблей,
        board - игровая доска(создана в формате списка)
        ship_list - список занятых точек на доске(фиксирует корабли, контуры кораблей, промахи, попадания)
        alive_ship - список живых кораблей
        методы: __str__(возвращает игровое поле в виде строки),
        out(проверка попадания координат за пределы игрового поля, возвращает bool)
        contour(создает контур кораблей, координаты контура сохраняются в список кораблей на поле, в случае потопления корабля, отображает его контур на поле соперника)
        install_ship(создает корабль, записывает в ship_list и alive_ship)
        shot(воспроизводит выстрел, выводит результат выстрела на консоли, возвращает: True для продолжения хода/ False передает ход сопернику)
        begin(задает пустое значение ship_list)"""

    def __init__(self, size=6, hidden=False):
        self.size = size
        self.hidden = hidden

        self.count = 0

        self.board = [["0"] * size for i in range(size)]
        self.ship_list = []
        self.alive_ship = []

    def __str__(self):
        show_board = ""
        show_board += "  | 1 | 2 | 3 | 4 | 5 | 6 | "
        for i, row in enumerate(self.board):
            show_board += f"\n{i + 1} | {' | '.join(row)} | "

        if self.hidden:
            show_board = show_board.replace("■", "0")

        return show_board

    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots_ship:
            for dx, dy in near:
                actual = Dot(d.x + dx, d.y + dy)
                if not (self.out(actual)) and actual not in self.ship_list:
                    if verb:
                        self.board[actual.x][actual.y] = "."
                    self.ship_list.append(actual)

    def install_ship(self, ship):
        for d in ship.dots_ship:
            if self.out(d) or d in self.ship_list:
                raise WrongPositionShipException()
        for d in ship.dots_ship:
            self.board[d.x][d.y] = "■"
            self.ship_list.append(d)

        self.alive_ship.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.ship_list:
            raise RepeatHitException()

        self.ship_list.append(d)

        for ship in self.alive_ship:
            if d in ship.dots_ship:
                ship.dot_hp -= 1
                self.board[d.x][d.y] = "X"
                if ship.dot_hp == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль потоплен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True

        self.board[d.x][d.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.ship_list = []


class Player:
    """Класс игрока, атрибуты:
        board - доска игрока
        enemy - доска соперника
        методы: ask(запрашивает координаты выстрела, реализуется в классах-потомках),
        move(запускает ход игрока)"""

    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except Exceptions as e:
                print(e)


class Computer(Player):
    """Класс компьютера, наследуется от Player,
        методы: переопределяет ask(генерирует рандомные координаты выстрела, возвращает координаты)"""

    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    """Класс пользователя, наследуется от Player,
        методы: переопределяет ask(запрашивает ввод координат выстрела на консоли, возвращает координаты)"""

    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Нужно ввести 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Нужно ввести числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    """Класс игры, атрибуты:
        size - размер доски
        pl - доска пользователя
        co - доска компьютера
        comp - экземпляр класса компьютер
        us - экземпляр класса пользователь

        методы: try_board(заполняет игровое поле кораблями в случайном порядке, отлавливает исключения)
        random_board(запускает заполнение игрового поля)
        welcome(выводит приветствие для пользователя)
        logic_game(выполняет последовательность игровых событий)
        start(запускает игру)"""
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hidden = True

        self.comp = Computer(co, pl)
        self.us = User(pl, co)

    def welcome(self):
        print("_" * 65)
        print(" Добро пожаловать в игру морской бой!       ")
        print("_" * 65)
        print(" формат ввода: x - номер строки, y - номер столбца")
        print("_" * 65)
        print(" легенда: X - попадание, T - промах, . - контур корабля")
        print("_" * 65)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = GameBoard(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.install_ship(ship)
                    break
                except WrongPositionShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board


    def logic_game(self):
        num = 0
        while True:
            us_board_lines = str(self.us.board).splitlines()
            comp_board_lines = str(self.comp.board).splitlines()
            print("")
            print("Доска пользователя:" + " " * 20 + "Доска компьютера:")

            for us_line, comp_line in zip(us_board_lines, comp_board_lines):
                print(us_line + " " * 10 + comp_line)

            print("_" * 65)
            if num % 2 == 0:
                print("Ход пользователя")
                repeat = self.us.move()
            else:
                print("Ход компьютера")
                repeat = self.comp.move()
            if repeat:
                num -= 1

            if self.comp.board.count == 7:
                print("_" * 27)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("_" * 27)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.welcome()
        self.logic_game()


sea_battle = Game()
sea_battle.start()