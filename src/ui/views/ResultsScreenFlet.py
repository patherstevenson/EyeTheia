import csv

import flet as ft
import flet.canvas as cv
from experiments.wordExperiment.GazePoint import GazePoint
from experiments.wordExperiment.GroupResults import GroupResults
from experiments.wordExperiment.WordGroup import WordGroup
from playsound3 import playsound
from ui.AppState import AppState
from ui.FletUtils import saveResultsToCSV, loadCSV
from utils.config import SCREEN_HEIGHT, SCREEN_WIDTH


def tabWidget(data, size, font: ft.FontWeight, spacing, border_width, border_color, is_score: bool = False):
    words = []
    for o in data:
        words.append(str(o))

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text(words[0], size=size, weight=font),
                              ft.Text(words[1], size=size, weight=font)],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,

                ),
                ft.Row(
                    controls=[ft.Text(words[2], size=size, weight=font),
                              ft.Text(words[3], size=size, weight=font)],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=spacing,
            data=is_score
        ),
        border=ft.Border.all(border_width, border_color),
        expand=1,
        aspect_ratio=1,
    )


def data_widget(res):
    # Data
    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(res.words.sound, size=20, weight=ft.FontWeight.W_600),
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            icon_color=ft.Colors.BLUE,
                            icon_size=40,
                            on_click=lambda _: playsound("src/experiments/wordExperiment/res/sounds/" + res.words.sound)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
                border=ft.Border.all(4, ft.Colors.GREY),
                expand=1
            )
            ,
            ft.Row(
                controls=[
                    tabWidget(res.gaze_score, 18, ft.FontWeight.W_600, 8, 4, ft.Colors.GREY),
                    ft.Column(
                        controls=[
                            ft.Text(str(res.gaze_score[4]) + " gazes failed", size=14, weight=ft.FontWeight.W_600,
                                    overflow=ft.TextOverflow.FADE),
                            ft.Divider(height=9, thickness=3),
                            ft.Text(f"{round(res.total_time, 2)} seconds to choose", size=14, weight=ft.FontWeight.W_600,
                                    overflow=ft.TextOverflow.FADE),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    )

                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=1
            )
        ],
        expand=1,
        aspect_ratio=1
    )


def switch_infos(word_tab_widget, res: GroupResults, page):
    if (word_tab_widget.content.data):
        word_tab_widget.content = tabWidget(res.words.words, 24, ft.FontWeight.W_600, 16, 6, ft.Colors.GREY,
                                            False).content
        page.update()
    else:
        word_tab_widget.content = points_canva(page, res)
        page.update()

    word_tab_widget.on_click = lambda _: switch_infos(word_tab_widget, res, page)


def res_widget(page, res):
    word_tab_widget = tabWidget(res.words.words, 24, ft.FontWeight.W_600, 16, 6, ft.Colors.GREY)

    word_tab_widget.aspect_ratio = 1
    word_tab_widget.ink = True

    word_tab_widget.on_click = lambda _: switch_infos(word_tab_widget, res, page)

    res_data_widget = data_widget(res)

    # Group Result
    return ft.Container(
        content=ft.Row(
            controls=[
                # TabWidget : Words
                word_tab_widget,
                ft.VerticalDivider(width=9, thickness=3),
                res_data_widget
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER, expand_loose=True,
            spacing=50,
        ),
        border=ft.Border.all(10, ft.Colors.AMBER_100),
        expand=1,
        margin=ft.Margin.symmetric(horizontal=20)
    )


canva_width = 0
canva_height = 0

canvas = []


def points_canva(page, res):
    canva = cv.Canvas(
        # data=True,
        # width=200,
        # height=200,
        on_resize=handle_resize,
        data=(res, page)
    )

    canvas.append(canva)

    return ft.Container(content=canva,
                        border=ft.Border.all(6, ft.Colors.GREY),
                        expand=1,
                        aspect_ratio=1,
                        data=True)


def handle_resize(e):
    canva_width: float = e.width
    canva_height: float = e.height

    (res, page) = e.control.data

    stroke_paint = ft.Paint(stroke_width=2, style=ft.PaintingStyle.STROKE)
    shapes = []

    old_x = -1
    old_y = -1

    style = ft.TextStyle(size=10)

    for pt in res.gaze_points:

        x = round((pt.x / SCREEN_WIDTH) * canva_width)
        y = round((pt.y / SCREEN_HEIGHT) * canva_height)
        shapes.append(cv.Circle(x=x, y=y, radius=10, paint=stroke_paint))
        shapes.append(cv.Text(x=x, y=y, value=str(pt.index), style=style, alignment=ft.Alignment.CENTER))
        if (old_x >= 0 & old_y >= 0):
            shapes.append(cv.Line(paint=stroke_paint, x1=old_x, y1=old_y, x2=x, y2=y))
        old_x = x
        old_y = y

    e.control.shapes = shapes

    page.update()


def ResultScreenView(page: ft.Page, state: AppState):
    if state.results == []:
        state.results = [
            GroupResults(0, WordGroup(["orange", "blouse", "pas", "bas"], "pas", "pronunciation_fr_pas.mp3"), 1),
            GroupResults(1, WordGroup(["permis", "feutre", "peine", "beine"], "peine", "pronunciation_fr_peine.mp3"),
                         2),
            GroupResults(2, WordGroup(["trait", "rond", "poule", "boule"], "poule", "pronunciation_fr_poule.mp3"), 0),
            GroupResults(3, WordGroup(["bas", "blouse", "pas", "orange"], "bas", "pronunciation_fr_bas.mp3"), 3),
            GroupResults(4, WordGroup(["beine", "feutre", "peine", "permis"], "beine", "pronunciation_fr_beine.mp3"),
                         1),
            GroupResults(5, WordGroup(["boule", "rond", "poule", "trait"], "boule", "pronunciation_fr_boule.mp3"), 2),

        ]
        state.results[0].gaze_score = [1, 5, 2, 7, 3]
        state.results[1].gaze_score = [1, 0, 4, 19, 20]
        state.results[2].gaze_score = [7, 2, 18, 7, 0]
        state.results[3].gaze_score = [1, 9, 4, 7, 0]
        state.results[4].gaze_score = [6, 2, 24, 6, 14]
        state.results[5].gaze_score = [14, 2, 4, 0, 7]

        state.results[0].gaze_points = [GazePoint(0, 791, 704), GazePoint(1, 902, 756), GazePoint(2, 864, 740),
                                        GazePoint(3, 887, 739), GazePoint(4, 917, 733), GazePoint(5, 884, 1025),
                                        GazePoint(6, 974, 1055), GazePoint(7, 891, 924), GazePoint(8, 841, 794),
                                        GazePoint(9, 851, 745), GazePoint(10, 750, 731), GazePoint(11, 777, 688),
                                        GazePoint(12, 779, 640), GazePoint(13, 783, 625), GazePoint(14, 797, 622),
                                        GazePoint(15, 770, 622), GazePoint(16, 774, 618), GazePoint(17, 900, 623),
                                        GazePoint(18, 795, 619), GazePoint(19, 775, 617), GazePoint(20, 744, 618),
                                        GazePoint(21, 720, 623), GazePoint(22, 718, 634), GazePoint(23, 671, 640),
                                        GazePoint(24, 615, 644), GazePoint(25, 556, 642), GazePoint(26, 511, 638),
                                        GazePoint(27, 486, 639), GazePoint(28, 474, 642), GazePoint(29, 427, 635),
                                        GazePoint(30, 475, 667), GazePoint(31, 500, 642), GazePoint(32, 429, 630),
                                        GazePoint(33, 416, 581), GazePoint(34, 398, 574), GazePoint(35, 345, 469),
                                        GazePoint(36, 377, 438), GazePoint(37, 361, 437), GazePoint(38, 346, 405),
                                        GazePoint(39, 424, 399), GazePoint(40, 448, 414), GazePoint(41, 417, 412),
                                        GazePoint(42, 413, 417), GazePoint(43, 418, 419), GazePoint(44, 405, 418),
                                        GazePoint(45, 379, 429), GazePoint(46, 384, 438), GazePoint(47, 386, 443),
                                        GazePoint(48, 372, 448), GazePoint(49, 381, 461), GazePoint(50, 395, 485),
                                        GazePoint(51, 398, 484), GazePoint(52, 398, 489), GazePoint(53, 429, 651),
                                        GazePoint(54, 434, 687), GazePoint(55, 434, 687), GazePoint(56, 434, 686),
                                        GazePoint(57, 434, 687), GazePoint(58, 431, 671), GazePoint(59, 424, 669),
                                        GazePoint(60, 423, 679), GazePoint(61, 423, 677), ]
        state.results[1].gaze_points = [GazePoint(0, 451, 601), GazePoint(1, 454, 554), GazePoint(2, 475, 597),
                                        GazePoint(3, 490, 589), GazePoint(4, 488, 623), GazePoint(5, 517, 644),
                                        GazePoint(6, 495, 658), GazePoint(7, 521, 673), GazePoint(8, 529, 672),
                                        GazePoint(9, 534, 672), GazePoint(10, 554, 674), GazePoint(11, 603, 681),
                                        GazePoint(12, 630, 688), GazePoint(13, 607, 689), GazePoint(14, 613, 690),
                                        GazePoint(15, 608, 682), GazePoint(16, 629, 682), GazePoint(17, 626, 681),
                                        GazePoint(18, 628, 680), GazePoint(19, 624, 680), GazePoint(20, 624, 679),
                                        GazePoint(21, 624, 679), GazePoint(22, 639, 655), GazePoint(23, 614, 657),
                                        GazePoint(24, 645, 683), GazePoint(25, 626, 658), GazePoint(26, 658, 671),
                                        GazePoint(27, 659, 672), GazePoint(28, 660, 671), GazePoint(29, 668, 669),
                                        GazePoint(30, 674, 667), GazePoint(31, 753, 650), GazePoint(32, 759, 646),
                                        GazePoint(33, 773, 646), GazePoint(34, 770, 646), GazePoint(35, 765, 646),
                                        GazePoint(36, 735, 692), GazePoint(37, 502, 629), GazePoint(38, 402, 548),
                                        GazePoint(39, 386, 511), GazePoint(40, 405, 463), GazePoint(41, 418, 427),
                                        GazePoint(42, 411, 426), GazePoint(43, 410, 426), GazePoint(44, 415, 434),
                                        GazePoint(45, 419, 439), GazePoint(46, 439, 442), GazePoint(47, 434, 454),
                                        GazePoint(48, 335, 491), GazePoint(49, 411, 592), GazePoint(50, 420, 609),
                                        GazePoint(51, 433, 617), GazePoint(52, 432, 615), GazePoint(53, 426, 543),
                                        GazePoint(54, 301, 489), GazePoint(55, 301, 488), GazePoint(56, 301, 488),
                                        GazePoint(57, 294, 474), GazePoint(58, 306, 471), GazePoint(59, 303, 469),
                                        GazePoint(60, 323, 446), ]
        state.results[2].gaze_points = [GazePoint(0, 383, 443), GazePoint(1, 494, 406), GazePoint(2, 512, 433),
                                        GazePoint(3, 502, 417), GazePoint(4, 505, 413), GazePoint(5, 505, 443),
                                        GazePoint(6, 519, 444), GazePoint(7, 532, 447), GazePoint(8, 540, 449),
                                        GazePoint(9, 553, 477), GazePoint(10, 572, 525), GazePoint(11, 703, 738),
                                        GazePoint(12, 892, 869), GazePoint(13, 625, 752), GazePoint(14, 706, 607),
                                        GazePoint(15, 618, 660), GazePoint(16, 615, 657), GazePoint(17, 615, 651),
                                        GazePoint(18, 685, 643), GazePoint(19, 738, 611), GazePoint(20, 863, 563),
                                        GazePoint(21, 905, 540), GazePoint(22, 1083, 550), GazePoint(23, 1066, 531),
                                        GazePoint(24, 838, 561), GazePoint(25, 812, 566), GazePoint(26, 674, 566),
                                        GazePoint(27, 543, 541), GazePoint(28, 456, 533), GazePoint(29, 459, 522),
                                        GazePoint(30, 426, 488), GazePoint(31, 441, 468), GazePoint(32, 453, 438),
                                        GazePoint(33, 442, 442), GazePoint(34, 434, 443), GazePoint(35, 442, 435),
                                        GazePoint(36, 445, 445), GazePoint(37, 455, 447), GazePoint(38, 499, 451),
                                        GazePoint(39, 475, 456), GazePoint(40, 481, 446), GazePoint(41, 447, 447),
                                        GazePoint(42, 405, 453), GazePoint(43, 420, 455), GazePoint(44, 413, 457),
                                        GazePoint(45, 409, 461), GazePoint(46, 406, 465), GazePoint(47, 401, 466),
                                        GazePoint(48, 393, 471), GazePoint(49, 399, 482), GazePoint(50, 395, 494),
                                        GazePoint(51, 402, 512), GazePoint(52, 421, 587), GazePoint(53, 418, 610),
                                        GazePoint(54, 422, 604), GazePoint(55, 424, 601), GazePoint(56, 417, 601),
                                        GazePoint(57, 415, 601), GazePoint(58, 463, 599), GazePoint(59, 447, 608),
                                        GazePoint(60, 429, 618), GazePoint(61, 428, 618), GazePoint(62, 430, 617),
                                        GazePoint(63, 426, 618), GazePoint(64, 432, 620), GazePoint(65, 432, 620), ]
        state.results[3].gaze_points = [GazePoint(0, 494, 574), GazePoint(1, 493, 561), GazePoint(2, 491, 551),
                                        GazePoint(3, 483, 549), GazePoint(4, 493, 548), GazePoint(5, 493, 555),
                                        GazePoint(6, 589, 709), GazePoint(7, 644, 731), GazePoint(8, 643, 701),
                                        GazePoint(9, 644, 667), GazePoint(10, 697, 645), GazePoint(11, 635, 601),
                                        GazePoint(12, 611, 579), GazePoint(13, 614, 578), GazePoint(14, 613, 578),
                                        GazePoint(15, 614, 579), GazePoint(16, 613, 579), GazePoint(17, 653, 583),
                                        GazePoint(18, 598, 664), GazePoint(19, 581, 671), GazePoint(20, 565, 670),
                                        GazePoint(21, 505, 693), GazePoint(22, 489, 696), GazePoint(23, 475, 704),
                                        GazePoint(24, 438, 727), GazePoint(25, 490, 736), GazePoint(26, 592, 712),
                                        GazePoint(27, 878, 722), GazePoint(28, 1256, 759), GazePoint(29, 1458, 758),
                                        GazePoint(30, 1483, 747), GazePoint(31, 1502, 748), GazePoint(32, 1500, 726),
                                        GazePoint(33, 1548, 763), GazePoint(34, 1535, 798), GazePoint(35, 1546, 788),
                                        GazePoint(36, 1549, 788), GazePoint(37, 1539, 789), GazePoint(38, 1543, 784),
                                        GazePoint(39, 1586, 728), GazePoint(40, 1638, 598), GazePoint(41, 1653, 474),
                                        GazePoint(42, 1561, 429), GazePoint(43, 1571, 421), GazePoint(44, 1634, 370),
                                        GazePoint(45, 1541, 429), GazePoint(46, 1608, 401), GazePoint(47, 1560, 412),
                                        GazePoint(48, 1550, 371), GazePoint(49, 1510, 425), GazePoint(50, 1506, 408),
                                        GazePoint(51, 1505, 403), GazePoint(52, 1504, 399), GazePoint(53, 1522, 389),
                                        GazePoint(54, 1529, 390), ]
        state.results[4].gaze_points = [GazePoint(0, 1507, 412), GazePoint(1, 1515, 409), GazePoint(2, 1512, 414),
                                        GazePoint(3, 1458, 423), GazePoint(4, 1396, 436), GazePoint(5, 1371, 443),
                                        GazePoint(6, 1335, 474), GazePoint(7, 1274, 505), GazePoint(8, 1272, 508),
                                        GazePoint(9, 1253, 556), GazePoint(10, 1212, 638), GazePoint(11, 1131, 911),
                                        GazePoint(12, 1131, 871), GazePoint(13, 1141, 835), GazePoint(14, 1148, 802),
                                        GazePoint(15, 1148, 730), GazePoint(16, 1036, 650), GazePoint(17, 1040, 623),
                                        GazePoint(18, 1054, 622), GazePoint(19, 1093, 614), GazePoint(20, 1102, 590),
                                        GazePoint(21, 1109, 585), GazePoint(22, 1083, 559), GazePoint(23, 586, 627),
                                        GazePoint(24, 543, 616), GazePoint(25, 405, 574), GazePoint(26, 355, 537),
                                        GazePoint(27, 315, 492), GazePoint(28, 334, 450), GazePoint(29, 365, 439),
                                        GazePoint(30, 386, 415), GazePoint(31, 391, 406), GazePoint(32, 381, 405),
                                        GazePoint(33, 382, 405), GazePoint(34, 386, 398), GazePoint(35, 364, 366),
                                        GazePoint(36, 345, 362), GazePoint(37, 298, 355), GazePoint(38, 274, 278),
                                        GazePoint(39, 220, 277), GazePoint(40, 270, 280), GazePoint(41, 229, 272),
                                        GazePoint(42, 231, 289), GazePoint(43, 217, 297), GazePoint(44, 217, 297),
                                        GazePoint(45, 218, 297), GazePoint(46, 218, 297), GazePoint(47, 218, 297),
                                        GazePoint(48, 219, 299), GazePoint(49, 221, 303), GazePoint(50, 227, 323),
                                        GazePoint(51, 261, 306), GazePoint(52, 281, 318), GazePoint(53, 272, 327),
                                        GazePoint(54, 332, 325), GazePoint(55, 317, 326), GazePoint(56, 293, 322),
                                        GazePoint(57, 292, 323), GazePoint(58, 292, 322), GazePoint(59, 291, 322), ]
        state.results[5].gaze_points = [GazePoint(0, 273, 309), GazePoint(1, 288, 330), GazePoint(2, 250, 321),
                                        GazePoint(3, 244, 342), GazePoint(4, 248, 344), GazePoint(5, 276, 343),
                                        GazePoint(6, 347, 343), GazePoint(7, 378, 350), GazePoint(8, 414, 348),
                                        GazePoint(9, 400, 344), GazePoint(10, 408, 352), GazePoint(11, 381, 354),
                                        GazePoint(12, 369, 360), GazePoint(13, 369, 358), GazePoint(14, 367, 360),
                                        GazePoint(15, 394, 364), GazePoint(16, 416, 385), GazePoint(17, 419, 386),
                                        GazePoint(18, 438, 390), GazePoint(19, 446, 388), GazePoint(20, 436, 393),
                                        GazePoint(21, 434, 391), GazePoint(22, 439, 389), GazePoint(23, 443, 388),
                                        GazePoint(24, 440, 390), GazePoint(25, 440, 390), GazePoint(26, 442, 393),
                                        GazePoint(27, 479, 387), GazePoint(28, 457, 400), GazePoint(29, 454, 413),
                                        GazePoint(30, 437, 439), GazePoint(31, 568, 532), GazePoint(32, 657, 533),
                                        GazePoint(33, 797, 538), GazePoint(34, 1097, 610), GazePoint(35, 1151, 603),
                                        GazePoint(36, 1135, 627), GazePoint(37, 1194, 712), GazePoint(38, 1225, 924),
                                        GazePoint(39, 1368, 1038), GazePoint(40, 1213, 996), GazePoint(41, 1141, 930),
                                        GazePoint(42, 1089, 763), GazePoint(43, 1132, 716), GazePoint(44, 1113, 721),
                                        GazePoint(45, 1186, 948), GazePoint(46, 1172, 1020), GazePoint(47, 1281, 1046),
                                        GazePoint(48, 1182, 1028), GazePoint(49, 1090, 998), GazePoint(50, 638, 705),
                                        GazePoint(51, 573, 609), GazePoint(52, 631, 670), GazePoint(53, 646, 805),
                                        GazePoint(54, 897, 799), GazePoint(55, 1000, 753), GazePoint(56, 1135, 684),
                                        GazePoint(57, 1190, 617), GazePoint(58, 1313, 537), GazePoint(59, 1354, 462),
                                        GazePoint(60, 1506, 407), GazePoint(61, 1463, 383), GazePoint(62, 1524, 367),
                                        GazePoint(63, 1257, 512), GazePoint(64, 1168, 511), GazePoint(65, 787, 368),
                                        GazePoint(66, 467, 309), GazePoint(67, 276, 291), GazePoint(68, 187, 304),
                                        GazePoint(69, 208, 314), GazePoint(70, 204, 308), GazePoint(71, 201, 302),
                                        GazePoint(72, 172, 334), GazePoint(73, 237, 276), GazePoint(74, 206, 272),
                                        GazePoint(75, 296, 327), GazePoint(76, 269, 384), GazePoint(77, 274, 393),
                                        GazePoint(78, 274, 393), GazePoint(79, 275, 394), GazePoint(80, 278, 401),
                                        GazePoint(81, 296, 508), GazePoint(82, 282, 554), GazePoint(83, 271, 500),
                                        GazePoint(84, 155, 462), GazePoint(85, 160, 355), GazePoint(86, 128, 322),
                                        GazePoint(87, 198, 329), GazePoint(88, 209, 329), GazePoint(89, 229, 328),
                                        GazePoint(90, 228, 323), GazePoint(91, 224, 320), GazePoint(92, 224, 320),
                                        GazePoint(93, 224, 320), GazePoint(94, 224, 320), GazePoint(95, 224, 319),
                                        GazePoint(96, 227, 316), ]

    widget_list = [
        res_widget(page, res)
        for res in state.results
    ]

    page.update()

    return ft.View(
        controls=[
            ft.ListView(controls=ft.Column(
                controls=widget_list,
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
                auto_scroll=True,
                height=page.height - 100, ),
            ft.Row(controls=[
                ft.Button(
                    content="Go Back To Main Menu",
                    on_click=lambda _: page.run_task(page.push_route, ("/"))
                ),
                ft.Button(
                    content="Save to CSV",
                    on_click=lambda _: page.run_task(saveResultsToCSV, state)
                ),
                ft.Button(
                    content="Load CSV",
                    on_click=lambda _: page.run_task(loadCSV, page)
                ),

            ]),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        # scroll=ft.ScrollMode.AUTO
    )