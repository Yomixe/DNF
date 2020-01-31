#!/usr/bin/python
# -*- coding:utf-8 -*-

#Przed uruchomieniem konieczne jest zainstalowanie modułu PySide2(przykładowo poprzez pip: pip install PySide2)

import sys
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QFileDialog, QMessageBox)


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Algorytm DNF")
        """Inicjlizacja zmiennych, na których będą dokynowane obliczenia oraz utworzenie obiektów
        (tabela,pola edycyjne,przyciski)"""
        self.table = QTableWidget()
        self.features = 0
        self.examples = 0
        self.file_name = QLineEdit()
        self.from_file = QPushButton("Wprowadź dane z pliku")
        self.solve = QPushButton("Rozwiąż")
        self.result = QLabel()
        self.error_info = QMessageBox()
        """Tworzenie layoutów a następnie dodawanie do nich widgetów"""
        self.left = QVBoxLayout()
        self.left.addWidget(self.from_file)
        self.left.addWidget(self.solve)
        self.left.addWidget(self.result)
        self.solve.setEnabled(False)
        self.center = QVBoxLayout()
        """Tworzenie  głównego layoutu a następnie dodawanie do nich trzech utworzonych wcześniej"""
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.left)
        self.layout.addLayout(self.center)
        self.setLayout(self.layout)
        """Komunikacja pomiędzy obiektami"""
        self.from_file.clicked.connect(self.create_table)



        self.solve.clicked.connect(self.DNF)


    """Tworzenie tabeli o ilości cech i przykładów podanych przez użytkownika i uzupełnianie jej wartościami z pliku"""

    @Slot()
    def create_table(self):
        try:
            self.file_name.setText(QFileDialog.getOpenFileName()[0])
            with open(self.file_name.text(), 'r') as f:
                for idx_line, line in enumerate(f):
                    self.examples = idx_line
                    for idx, item in enumerate(line.split(' ')):
                        self.features = idx - 1
            self.solve.setEnabled(True)
            self.table.setColumnCount(self.features + 1)
            self.table.setRowCount(self.examples)
            features = list(range(1, self.features + 1))
            features = ["f" + str(x) for x in features]
            self.table.setHorizontalHeaderItem(self.features, QTableWidgetItem("Etykieta"))
            self.table.setHorizontalHeaderLabels(features)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.center.addWidget(self.table)

            with open(self.file_name.text(), 'r') as f:
                for idx_line, line in enumerate(f):
                    for idx, item in enumerate(line.split(' ')):
                        self.table.setItem(idx_line, idx, QTableWidgetItem(str(item)))

        except FileNotFoundError:
            self.error_info.setWindowTitle("Uwaga!")
            self.error_info.setText("Nie wybrabrano pliku.")
            self.error_info.exec()




    """Konwertowanie obiektowej tabeli na listę D, na której będą dokonywane obliczenia"""

    def convert_to_lists(self):
        self.D = []
        ex = []
        try:
            for i in range(self.table.rowCount()):
                for j in range(self.table.columnCount()):
                    ex.append(int(self.table.item(i, j).text()))
                    if len(ex) == self.table.columnCount():
                        self.D.append(ex)
                        ex = []
                        break

        except:
            self.error_info.setWindowTitle("Uwaga!")
            self.error_info.setText("Uzupełnij poprawnie wszystkie pola w tabeli.")
            self.error_info.exec()

    """Algorytm DNF"""

    @Slot()
    def DNF(self):
        self.convert_to_lists()
        P = [self.D[i] for i in range(len(self.D)) if self.D[i][-1] == 1]
        h = []
        fail = 0
        while P != [[-1] * len(P[i]) for i in range(len(P))] and fail == 0:
            N = [self.D[i] for i in range(len(self.D)) if self.D[i][-1] == 0]
            r = []
            while N != [[-1] * len(N[i]) for i in range(len(N))] and fail == 0:
                chosen_index = self.find_f(P, N)
                r.append(chosen_index)
                self.clear_negative_rows(chosen_index, N)
                if len(r) != len(set(r)):
                    fail = 1
            if self.clear_positive_rows(r, P) == 1:
                fail = 1
            r = ["f" + str(i + 1) for i in r]
            r = " ʌ ".join(r)
            h.append(r)
        self.get_solution(h, fail)

    def find_f(self, P, N):
        sum_p = list(self.sum_over_columns(P))
        sum_n = list(self.sum_over_columns(N))
        v = 0
        chosen_index = 0
        for i in range(len(sum_p)):
            if sum_n[i] == 0:
                sum_n[i] = 0.001
            if sum_p[i] // sum_n[i] > v:
                v = sum_p[i] // sum_n[i]
                chosen_index = i
        return chosen_index

    def sum_over_columns(self, tab):
        for i in range(len(tab[0]) - 1):
            count = 0
            for j in range(len(tab)):
                if tab[j][i] == 1:
                    count += 1
            yield count

    def clear_negative_rows(self, index, N):
        n = len(N)
        for i in range(n):
            if N[i][index] == 0:
                N[i] = [-1] * len(N[i])

    def clear_positive_rows(self, r, P ):
        n = len(P)
        mark = 0
        for i in range(n):
            sum = 0
            for j in r:
                if P[i][j] == 1:
                    sum += 1
            if sum == len(r):
                P[i] = [-1] * len(P[i])
                mark += 1
        if mark == 0:
            return 1
        return 0

    def get_solution(self, h, fail):
        if fail == 1:
            self.result.setText("Brak rozwiązania")
        else:
            self.result.setText("Rozwiązanie:\n\nh= (" + ") v (".join(h) + ")")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.resize(1000, 300)
    widget.show()
    sys.exit(app.exec_())
