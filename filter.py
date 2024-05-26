# class MySortFilterProxyModel(QSortFilterProxyModel):
#
#     Q_OBJECT
# # public
#     MySortFilterProxyModel(QObject parent = None)
#     QDate filterMinimumDate() { return minDate; }
#     def setFilterMinimumDate(date):
#     QDate filterMaximumDate() { return maxDate; }
#     def setFilterMaximumDate(date):
# # protected
#     bool filterAcceptsRow(int sourceRow, QModelIndex sourceParent) override
#     bool lessThan(QModelIndex left, QModelIndex right) override
# # private
#     dateInRange = bool(QDate date)
#     minDate = QDate()
#     maxDate = QDate()
