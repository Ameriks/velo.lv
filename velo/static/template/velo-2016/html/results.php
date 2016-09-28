<?php include_once('head.php'); ?>
<main>
    <div class="w100">
        <div class="inner">
            <form action="" class="w100 bgc-dgray border-right border-bottom border-left">
                <div class="w100 bottom-margin--20"></div>
                <div class="w100">
                    <div class="inner">
                        <div class="row row--gutters-20">
                            <div class="col-xl-12 col-m-24 bottom-margin--20">
                                <div class="input-wrap">
                                    <select
                                        class="select"
                                        name="year"
                                    >
                                        <option value="2014">2014. gada rezultāti</option>
                                        <option value="2015">2015. gada rezultāti</option>
                                        <option value="2016" selected>2016. gada rezultāti</option>
                                        <option value="2017">2017. gada rezultāti</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-xl-12 col-m-24 bottom-margin--20">
                                <div class="input-wrap">
                                    <select
                                        class="select"
                                        name="competition"
                                    >
                                        <option value="" selected>SEB maratons</option>
                                        <option value="">SEB maratons</option>
                                        <option value="">SEB maratons</option>
                                        <option value="">SEB maratons</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-xl-12 col-m-24 bottom-margin--20">
                                <div class="input-wrap">
                                    <select
                                        class="select"
                                        name="stage"
                                    >
                                        <option value="" selected>1. posms  -  valmiera, cēsis</option>
                                        <option value="">1. posms  -  valmiera, cēsis</option>
                                        <option value="">1. posms  -  valmiera, cēsis</option>
                                        <option value="">1. posms  -  valmiera, cēsis</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-xl-12 col-m-24 bottom-margin--20">
                                <div class="input-wrap">
                                    <select
                                        class="select"
                                        name="distance"
                                    >
                                        <option value="" selected>VIRŠI-A distance</option>
                                        <option value="">VIRŠI-A distance</option>
                                        <option value="">VIRŠI-A distance</option>
                                        <option value="">VIRŠI-A distance</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-xl-8 col-m-24 bottom-margin--20">
                                <div class="input-wrap">
                                    <input
                                        type="text"
                                        class="input-field if--50 if--dark"
                                        placeholder="Vārds Uzvārds"
                                    >
                                </div>
                            </div>
                            <div class="col-xl-8 col-m-24 bottom-margin--20">
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
                            <div class="col-xl-8 col-m-24 bottom-margin--20">
                                <button
                                    class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100" 
                                    type="submit"
                                >
                                    <div class="btn__flex">
                                        Meklēt
                                        <svg class="btn__icon icon">
                                            <use
                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                xlink:href="/img/icons.svg#arrow--right"></use>
                                        </svg>
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>               
            </form>
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
                                    <th>Gads</th>
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
                    <div class="layouts-results-download">
                        <a href="" class="layouts-results-download-btn btn btn--50 btn--blue btn--blue-hover btn--blue-active">
                            <div class="btn__flex">
                                Rezultātu fails
                                <svg class="fs20 icon left-margin--20">
                                    <use
                                        xmlns:xlink="http://www.w3.org/1999/xlink"
                                        xlink:href="/img/icons.svg#pdf"></use>
                                </svg>
                            </div>
                        </a>
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
    <?php include_once('pagination.php'); ?>
</main>
<?php include_once('foot.php'); ?>