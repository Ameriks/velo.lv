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
                                <a href="" class="btn btn--50 btn--dgray-transparent btn--blue-hover btn--blue-active active bottom-margin--20">
                                    DALĪBNIEKU KOPVERTĒJUMS
                                </a>
                            </div>
                            <div class="col-xl-12 col-m-24">
                                <a href="" class="btn btn--50 btn--dgray-transparent btn--blue-hover btn--blue-active bottom-margin--20">
                                    KOMANDU KOPVĒRTĒJUMS
                                </a>
                            </div>
                            <div class="col-xl-8 col-m-24 bottom-margin--20">
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
                                            placeholder="Meklēt braucēju"
                                        >
                                    </div>
                                </div>
                            </div>
                            <div class="col-xl-6 col-m-24 bottom-margin--20">
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
                            <div class="col-xl-6 col-m-24 bottom-margin--20">
                                <div class="input-wrap">
                                    <select
                                        class="select"
                                        name="group"
                                    >
                                        <option value="" selected>VISAS GRUPAS</option>
                                        <option value="">VISAS GRUPAS</option>
                                        <option value="">VISAS GRUPAS</option>
                                        <option value="">VISAS GRUPAS</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-xl-4 col-m-24 bottom-margin--20">
                                <a
                                    href=""
                                    download
                                    class="btn btn--50 border-left border-right border-top border-bottom btn--blue-hover btn--blue-active flex--important justify--center align-items--center"
                                >
                                    <div class="w100 flex--1 flex justify--center align-items--center">
                                        <svg class="fs20 c-white icon">
                                            <use
                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                xlink:href="/img/icons.svg#pdf"></use>
                                        </svg>
                                    </div>
                                </a>
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
                                    <th>Nr.</th>
                                    <th>Vieta</th>
                                    <th>Vārds</th>
                                    <th>Uzvārds</th>
                                    <th>
                                        Gads
                                        <svg class="table-block__sort-icon icon">
                                            <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#arrow--down"></use>
                                        </svg>
                                    </th>
                                    <th>Laiks</th>
                                    <th>Komanda</th>
                                    <th>1.</th>
                                    <th>2.</th>
                                    <th>3.</th>
                                    <th>4.</th>
                                    <th>5.</th>
                                    <th>6.</th>
                                    <th>7.</th>
                                    <th>Distance</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>163</td>
                                    <td>1</td>
                                    <td>Ainārs</td>
                                    <td>Priedeslaipa</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>ML-SERVISS / ŠĶĒPS</td>
                                    <td>716</td>
                                    <td>723</td>
                                    <td>0</td>
                                    <td>768</td>
                                    <td>755</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
                                </tr>
                                <tr>
                                    <td>209</td>
                                    <td>2</td>
                                    <td>Raivis</td>
                                    <td>Belohvoščiks</td>
                                    <td>1976</td>
                                    <td>RRS Imants</td>
                                    <td>Alpha Baltic/Unitymarathons.com</td>
                                    <td>784</td>
                                    <td>758</td>
                                    <td>821</td>
                                    <td>802</td>
                                    <td>842</td>
                                    <td>885</td>
                                    <td>0</td>
                                    <td>3332</td>
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