<?php include_once('head.php'); ?>
<main class="theme--green">
    <?php include_once('competition-primary-heading.php'); ?>
    <?php include_once('secondary-nav.php'); ?>   
    <div class="w100">
        <div class="inner">
            <div class="border-left border-right border-bottom">
                <?php include_once('competition-key-info.php'); ?>
            </div>
            <div class="w100 bgc-dgray border-right border-bottom border-left">
                <div class="w100 bottom-margin--20"></div>
                <div class="inner">
                    <form action="" class="w100">
                        <div class="row row--gutters-20">
                            <div class="col-xl-12 col-m-24">
                                <a href="" class="btn btn--50 btn--dgray-transparent btn--blue-hover btn--blue-active bottom-margin--20">
                                    DALĪBNIEKU KOPVERTĒJUMS
                                </a>
                            </div>
                            <div class="col-xl-12 col-m-24">
                                <a href="" class="btn btn--50 btn--dgray-transparent btn--blue-hover btn--blue-active active bottom-margin--20">
                                    KOMANDU KOPVĒRTĒJUMS
                                </a>
                            </div>
                            <div class="col-xl-14 col-s-24 bottom-margin--20">
                                <div class="right">
                                    <button class="btn btn--50 btn--square-50 btn--dblue btn--blue-hover btn--blue-active left-minus-1">
                                        <div class="w100 flex--1 flex justify--center align-items--center">
                                            <svg class="fs20 icon">
                                                <use
                                                    xmlns:xlink="http://www.w3.org/1999/xlink"
                                                    xlink:href="/img/icons.svg#search"></use>
                                            </svg>
                                        </div>
                                    </button>
                                </div>
                                <div class="context">
                                    <div class="input-wrap">
                                        <input
                                            type="text"
                                            class="input-field if--50 if--dark"
                                            placeholder="Meklēt komandu"
                                        >
                                    </div>
                                </div>
                            </div>
                            <div class="col-xl-10 col-s-24 bottom-margin--20">
                                <div class="input-wrap">
                                    <select
                                        class="select"
                                        name="distance"
                                    >
                                        <option value="" selected disabled>Distance</option>
                                        <option value="">VIRŠI-A distance</option>
                                        <option value="">VIRŠI-A distance</option>
                                        <option value="">VIRŠI-A distance</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <div class="w100">
        <div class="inner">
            <div class="w100 bgc-dgray border-right border-bottom border-left">
                <div class="inner">
                    <div class="drag-bar disable--select js-drag-bar">
                        <div class="drag-bar__handle  js-drag-handle">
                            <div class="drag-bar__handle-circle">
                                <svg class="drag-bar__handle-icon icon">
                                    <use
                                        xmlns:xlink="http://www.w3.org/1999/xlink"
                                        xlink:href="/img/icons.svg#stripes"></use>
                                </svg>
                            </div>
                             <div class="drag-bar__click-space"></div>
                        </div>
                    </div>
                </div>
            </div>             
        </div>
    </div>
    <div class="w100 relative js-scroll-along-block">
        <div class="inner">
            <div class="w100 bgc-dgray border-right border-left">
                <div class="drag-box js-drag-container">
                    <div class="drag-box__content  js-drag-content">
                        <table class="table-block">
                            <thead>
                                <tr>
                                    <th>Vieta</th>
                                    <th>Valsts</th>
                                    <th>
                                        Komanda
                                        <svg class="table-block__sort-icon icon">
                                            <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#arrow--down"></use>
                                        </svg>
                                    </th>
                                    <th>Kontaktpersona</th>
                                    <th>Dalībnieki</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="table-block__hightlight">
                                    <td>1.</td>
                                    <td>Latvija</td>
                                    <td><a href="">Alpha Baltic/Unitymarathons.com</a></td>
                                    <td>Raivis Belohvoščiks</td>
                                    <td>
                                        <a href="" class="w100 h100 text-align--center">
                                            <svg class="c-white fs20 icon">
                                                <use
                                                    xmlns:xlink="http://www.w3.org/1999/xlink"
                                                    xlink:href="/img/icons.svg#arrow--right"></use>
                                            </svg>
                                        </a>
                                    </td>
                                </tr>
                                <tr class="table-block__hightlight">
                                    <td>1.</td>
                                    <td>Latvija</td>
                                    <td><a href="">Alpha Baltic/Unitymarathons.com</a></td>
                                    <td>Raivis Belohvoščiks</td>
                                    <td>
                                        <a href="" class="w100 h100 text-align--center">
                                            <svg class="c-white fs20 icon">
                                                <use
                                                    xmlns:xlink="http://www.w3.org/1999/xlink"
                                                    xlink:href="/img/icons.svg#arrow--right"></use>
                                            </svg>
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>1.</td>
                                    <td>Latvija</td>
                                    <td><a href="">Alpha Baltic/Unitymarathons.com</a></td>
                                    <td>Raivis Belohvoščiks</td>
                                    <td>
                                        <a href="" class="w100 h100 text-align--center">
                                            <svg class="c-white fs20 icon">
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
                </div>
                <div class="w100 relative">
                    <div class="page-count">
                        <div class="table">
                            <div class="table-cell text-align--center">
                                50 no 1337
                            </div>
                        </div>
                    </div>
                </div>
            </div>            
        </div>
        <div class="scroll-along__container  js-scroll-along">
            <div class="scroll-along__element">
                <div class="inner">
                    <div class="drag-box scroll-along__borders  js-drag-container">
                        <div class="drag-box__content  js-drag-content js-scroll-append">
                            <!--Šeit nāk klonētā tabulas galva-->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="w100 flex--1"></div>
    <?php include_once('pagination.php'); ?>
</main>
<?php include_once('foot.php'); ?>