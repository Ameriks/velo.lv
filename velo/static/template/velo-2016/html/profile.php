<?php include_once('head.php'); ?>
<main>
    <div class="w100 flex">
        <div class="inner flex">
            <div class="w100 border-right border-left flex direction--column">
                <h1 class="heading w100 border-bottom fs21 flex wrap--nowrap direction--column justify--start align-items--center">
                    <span class="w100">Mans profils</span>
                    <span class="w100 c-yellow">andris.alps@velo.lv</span>
                </h1>
                <h2 class="heading heading--smaller w100 border-bottom fs21 flex wrap--nowrap direction--column justify--start align-items--center">
                    <span class="w100">MANA INFORMĀCIJA</span>
                </h2>
                <form action="" class="w100 bottom-margin--20  js-form">
                    <div class="row">
                        <div class="col-xl-9 col-m-24 layouts-profile-left">
                            <div class="w100 bottom-margin--20"></div>
                            <fieldset class="inner">
                                <div class="input-wrap w100 bottom-margin--15">
                                    <label for="input-1" class="w100 fs13 bottom-margin--10">E-pasts</label>
                                    <input
                                        type="email"
                                        class="input-field if--50 if--dark"
                                        id="input-1"
                                        name="input-1"
                                        value="andris.alps@velo.lv"
                                        data-rule-required="true"
                                        data-rule-email="true"
                                        data-msg-required="Šis lauks ir aizpildāms obligāti"
                                        data-msg-email="Lūdzu ievadiet derīgu e-pasta adresi!"
                                    >
                                </div>
                                <div class="input-wrap w100 bottom-margin--15">
                                    <label for="password" class="w100 fs13 bottom-margin--10">Parole</label>
                                    <input
                                        type="password"
                                        class="input-field if--50 if--dark  js-placeholder-up"
                                        id="password"
                                        name="password"
                                        value="test123"
                                        data-rule-required="true"
                                        data-msg-required="Šis lauks ir aizpildāms obligāti"
                                    >
                                </div>
                                <div class="input-wrap w100 bottom-margin--20">
                                    <label for="password_confirm" class="w100 fs13 bottom-margin--10">Parole atkārtoti</label>
                                    <input
                                        type="password"
                                        class="input-field if--50 if--dark  js-placeholder-up"
                                        id="password_confirm"
                                        name="password_confirm"
                                        value="test123"
                                        data-rule-required="true"
                                        data-rule-equalto="#password"
                                        data-msg-required="Šis lauks ir aizpildāms obligāti"
                                        data-msg-equalto="Paroles nesakrīt!"
                                    >
                                </div>
                                <div class="input-wrap w100 bottom-margin--20">
                                    <select
                                        class="select"
                                        name="country"
                                    >
                                        <option value="" selected>Igaunija</option>
                                        <option value="">Latvija</option>
                                        <option value="">Lietuva</option>
                                    </select>
                                </div>
                                <div class="input-wrap w100 bottom-margin--20">
                                    <select
                                        class="select"
                                        name="city"
                                    >
                                        <option value="" selected>Rīga</option>
                                        <option value="">Liepāja</option>
                                        <option value="">Daugavpils</option>
                                    </select>
                                </div>
                                <div class="input-wrap w100 bottom-margin--30">
                                    <select
                                        class="select"
                                        name="velo"
                                    >
                                        <option value="" selected>Trek</option>
                                        <option value="">Rockmachine</option>
                                        <option value="">Miranda</option>
                                    </select>
                                </div>
                            </fieldset>
                        </div>
                        <div class="col-xl-15 col-m-24 bgc-dgray relative">
                            <div class="w100 bottom-margin--20"></div>
                            <fieldset class="inner">
                                <div class="row row--gutters-20">
                                    <div class="col-xl-8 col-s-18">
                                        <p class="w100 fs13 bottom-margin--10">Profila attēls</p>
                                        <div
                                            class="layouts-profile-hero  js-background-image"
                                            data-background-image="/img/placeholders/velo-placeholder--1x1.svg"
                                        ></div>
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <div class="input-file">
                                                <input
                                                    type="file"
                                                    name="file-1[]"
                                                    id="file-1"
                                                    class="input-file__input  js-input-file"
                                                    data-filesize="8388608"
                                                />
                                                <label
                                                    for="file-1"
                                                    class="layouts-profile-image-input input-file__label btn btn--50 btn--dblue btn--blue-hover btn--blue-active w100  js-input-file__label"
                                                >
                                                    <span class="js-input-file__text">Mainīt bildi</span>
                                                </label>
                                                <p class="error hidden  js-input-file__error">Augšuplādējiet bildi kas ir mazāka par <span class="js-allowed-size">NN</span> MB</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-xl-16 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label for="input-2" class="w100 fs13 bottom-margin--10">Apraksts par sevi <span class="c-white--50">&nbsp;&nbsp;(max 300 simboli)</span></label>
                                            <textarea
                                                name="input-2"
                                                id="input-2"
                                                placeholder="Šeit uzrakstiet īsu aprakstu par sevi."
                                                class="layouts-profile-textarea input-field if--50 if--dark input-field--textarea w100"></textarea>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label for="input-3" class="w100 fs13 bottom-margin--10">Vārds</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark"
                                                id="input-3"
                                                name="input-3"
                                                value="Andris"
                                                data-rule-required="true"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label for="input-4" class="w100 fs13 bottom-margin--10">Uzvārds</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark"
                                                id="input-4"
                                                name="input-4"
                                                value="Alps"
                                                data-rule-required="true"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-24">
                                        <div class="input-wrap w100">
                                            <div class="w100 fs13 bottom-margin--10">Dzimšanas datums</div>
                                            <div class="w100">
                                                <div class="row row--gutters-20">
                                                    <div class="col-xl-8 col-s-24">
                                                        <select
                                                            class="select bottom-margin--20"
                                                            name="year"
                                                            data-rule-required="true"
                                                            data-msg-required="Lūdzu ievadiet savu dzimšanas gadu"
                                                        >
                                                            <option value="" selected disabled>Gads</option>
                                                            <option value="">1989</option>
                                                            <option value="">1988</option>
                                                            <option value="">1987</option>
                                                        </select>
                                                    </div>
                                                    <div class="col-xl-8 col-s-24">
                                                        <select
                                                            class="select bottom-margin--20"
                                                            name="month"
                                                            data-rule-required="true"
                                                            data-msg-required="Lūdzu ievadiet savu dzimšanas mēnesi"
                                                        >
                                                            <option value="" selected disabled>Mēnesis</option>
                                                            <option value="">Jānvāris</option>
                                                            <option value="">Februāris</option>
                                                            <option value="">Marts</option>
                                                        </select>
                                                    </div>
                                                    <div class="col-xl-8 col-s-24">
                                                        <select
                                                            class="select bottom-margin--20"
                                                            name="day"
                                                            data-rule-required="true"
                                                            data-msg-required="Lūdzu ievadiet savu dzimšanas dienu"
                                                        >
                                                            <option value="" selected disabled>Diena</option>
                                                            <option value="">1</option>
                                                            <option value="">2</option>
                                                            <option value="">3</option>
                                                            <option value="">31</option>
                                                        </select>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label for="input-8" class="w100 fs13 bottom-margin--10">Telefona numurs</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-8"
                                                name="input-8"
                                                value="12334562"
                                                data-rule-number="true"
                                                data-msg-number="Lūdzu ievadiet tikai ciparus"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-24">
                                        <div class="input-wrap w100 bottom-margin--30">
                                            <div class="checkbox bottom-margin--15">
                                                <input class="checkbox__input" type="checkbox" id="checkbox-1" value="" checked="">
                                                <label for="checkbox-1" class="checkbox__label">
                                                    <div class="flex wrap--nowrap direction--row justify--start align-items--center">
                                                        <svg class="checkbox__graphic checkbox__graphic--default icon">
                                                            <use
                                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                                xlink:href="/img/icons.svg#checkbox--default"></use>
                                                        </svg>
                                                        <svg class="checkbox__graphic checkbox__graphic--checked icon">
                                                            <use
                                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                                xlink:href="/img/icons.svg#checkbox--checked"></use>
                                                        </svg>
                                                        <span class="checkbox__text">Vēlos saņemt velo.lv jaunumus e-pastā</span>
                                                    </div>
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </fieldset>
                            <div class="announcement flex wrap--nowrap direction--row justify--center align-items--center">
                                <div class="announcement__decoration">
                                    <svg class="announcement__icon icon">
                                       <use
                                           xmlns:xlink="http://www.w3.org/1999/xlink"
                                           xlink:href="/img/icons.svg#tick"></use>
                                    </svg>
                                </div>
                                <div class="announcement__text">IZmaiņas saglabātas!</div>
                            </div>
                        </div>
                        <div class="col-xl-24 border-top border-bottom">
                            <div class="row">
                                <div class="col-xl-18 col-m-14 col-s-24"></div>
                                <div class="col-xl-6 col-m-10 col-s-24">
                                    <button class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100">
                                        Saglabāt
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>