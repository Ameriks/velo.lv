<?php include_once('head.php'); ?>
<main>
    <div class="w100 flex">
        <div class="inner flex">
            <div class="w100 border-right border-left flex--1">
                <h1 class="heading w100 border-bottom fs21 flex wrap--nowrap direction--column justify--start align-items--center">
                    <span class="w100">Mans profils</span>
                    <span class="w100 c-yellow">andris.alps@velo.lv</span>
                </h1>
                <div class="w100 bgc-dgray flex--1">
                    <h2 class="heading heading--smaller w100 border-bottom fs21 flex wrap--nowrap direction--column justify--start align-items--center">
                        <span class="w100">MANI PIETEIKUMI</span>
                    </h2>
                    <div class="w100 overflow--auto border-bottom bottom-margin--20">
                        <table class="table-block">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Sacensība</th>
                                    <th>
                                        Pieteikts
                                        <svg class="table-block__sort-icon icon">
                                            <use
                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                xlink:href="/img/icons.svg#arrow--down"></use>
                                        </svg>
                                    </th>
                                    <th>Statuss</th>
                                    <th>Maksāt</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>53941</td>
                                    <td>SEB MTB MARATONS, Virši-A distance</td>
                                    <td>4.03.2016 17:05</td>
                                    <td>Nav apmaksāts</td>
                                    <td>
                                        <a href="" class="fs12 fw700 uppercase c-white w100 flex direction--row justify--center align-items--center">
                                            Maksāt
                                            <svg class="icon fs14 left-margin--10">
                                                <use
                                                    xmlns:xlink="http://www.w3.org/1999/xlink"
                                                    xlink:href="/img/icons.svg#arrow--right"></use>
                                            </svg>
                                        </a>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <h2 class="heading heading--smaller w100 border-top border-bottom fs21 flex wrap--nowrap direction--column justify--start align-items--center">
                        <span class="w100">Rezultāti</span>
                    </h2>
                    <div class="w100 overflow--auto border-bottom bottom-margin--20">
                        <table class="table-block">
                            <thead>
                                <tr>
                                    <th>Gads</th>
                                    <th>
                                        Sacensība
                                        <svg class="table-block__sort-icon icon">
                                            <use
                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                xlink:href="/img/icons.svg#arrow--down"></use>
                                        </svg>
                                    </th>
                                    <th>Vieta</th>
                                    <th>Komanda</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>2016</td>
                                    <td>SEB MTB MARATONS, Virši-A distance</td>
                                    <td>5.</td>
                                    <td>INFOERA DION CYCLING</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>