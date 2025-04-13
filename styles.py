MAIN_STYLE = """
QWidget {
    background-color: #1E1E1E;
    color: #FFFFFF;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 10pt;
}

QLabel {
    color: #FFFFFF;
}

QLineEdit, QComboBox, QPushButton {
    background-color: #2D2D2D;
    border: 1px solid #3E3E3E;
    border-radius: 4px;
    padding: 8px;
    color: #FFFFFF;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #E32636;
}

QPushButton {
    background-color: #E32636;
    color: white;
    border: none;
    font-weight: bold;
    min-height: 36px;
}

QPushButton:hover {
    background-color: #FF3546;
}

QPushButton:pressed {
    background-color: #C41E2E;
}

QPushButton:disabled {
    background-color: #4D4D4D;
    color: #8D8D8D;
}

QComboBox::drop-down {
    border: 0px;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(resources/icons/dropdown.png);
    width: 14px;
    height: 14px;
}

QComboBox QAbstractItemView {
    background-color: #2D2D2D;
    border: 1px solid #3E3E3E;
    selection-background-color: #E32636;
}

QProgressBar {
    border: 1px solid #3E3E3E;
    border-radius: 4px;
    text-align: center;
    background-color: #2D2D2D;
}

QProgressBar::chunk {
    background-color: #E32636;
    width: 10px;
    margin: 0.5px;
}

#urlInput {
    min-height: 40px;
    font-size: 11pt;
}

#downloadBtn {
    min-height: 40px;
    font-size: 11pt;
}

#titleLabel {
    font-size: 20pt;
    color: #E32636;
    font-weight: bold;
}

#statusLabel {
    color: #AAAAAA;
}
"""