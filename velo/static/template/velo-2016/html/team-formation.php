<?php include_once('head.php'); ?>
    <main>
        <div class="w100 flex">
            <div class="inner flex">
                <div class="w100 border-right border-left no-border--560">
                    <h1 class="heading w100 border-bottom fs21 flex wrap--nowrap direction--column justify--start align-items--center">
                        <span class="w100">Mans profils</span>
                        <span class="w100 c-yellow">andris.alps@velo.lv</span>
                    </h1>
                    <p class="heading heading--smaller w100 border-bottom fs21 flex wrap--nowrap direction--column justify--start align-items--center">
                        <span class="w100">Komandas izveide</span>
                    </p>
                    <form action="" class="w100 bgc-dgray js-form">
                        <div class="w100">
                            <div class="inner no-padding--560">
                                <div class="row row--gutters-50">
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                            <select
                                                class="select"
                                                name="distance"
                                                id="distance"
                                                data-rule-required="true"
                                                data-msg-required="Lūdzu izvēlaties kādu no sacensībām"
                                            >
                                                <option selected disabled>Distance</option>
                                                <option value="1">1</option>
                                                <option value="2">2</option>
                                                <option value="3">3</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--15">
                                            <label
                                                for="input-1"
                                                class="input-field-label  js-placeholder"
                                            >Kontaktpersona *</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-1"
                                                name="input-1"
                                                data-rule-required="true"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--15">
                                            <label
                                                for="input-2"
                                                class="input-field-label  js-placeholder"
                                            >Komandas nosaukums *</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-2"
                                                name="input-2"
                                                data-rule-required="true"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label
                                                for="input-3"
                                                class="input-field-label  js-placeholder"
                                            >E-pasts</label>
                                            <input
                                                type="email"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-3"
                                                name="input-3"
                                                data-rule-email="true"
                                                data-msg-email="Lūdzu ievadiet derīgu e-pasta adresi!"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                            <select
                                                class="select"
                                                name="country"
                                                id="country"
                                                data-rule-required="true"
                                                data-msg-required="Lūdzu izvēlaties kādu no sacensībām"
                                            >
                                                <option selected disabled>Valsts</option>
                                                <option value="1">1</option>
                                                <option value="2">2</option>
                                                <option value="3">3</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label
                                                for="input-4"
                                                class="input-field-label  js-placeholder"
                                            >Telefona numurs *</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-4"
                                                name="input-4"
                                                data-rule-required="true"
                                                data-msg-required="Lūdzu izvēlaties kādu no sacensībām"
                                                data-rule-number="true"
                                                data-msg-number="Lūdzu ievadiet tikai ciparus"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label
                                                for="description"
                                                class="input-field-label  js-placeholder"
                                            >Apraksts</label>
                                            <textarea
                                                name="description"
                                                id="description"
                                                class="input-field if--50 if--dark input-field--textarea  js-placeholder-up"
                                            ></textarea>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label
                                                for="info"
                                                class="input-field-label  js-placeholder"
                                            >Apkalpes informācija</label>
                                            <textarea
                                                name="info"
                                                id="info"
                                                class="input-field if--50 if--dark input-field--textarea  js-placeholder-up"
                                            ></textarea>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <div class="input-file">
                                                <input
                                                    type="file"
                                                    name="file-1[]"
                                                    id="file-1"
                                                    class="input-file__input  js-input-file"
                                                    data-filesize="8388608"
                                                >
                                                <label
                                                    for="file-1"
                                                    class="layouts-profile-image-input input-file__label btn btn--50 btn--dblue btn--blue-hover btn--blue-active w100  js-input-file__label"
                                                >
                                                    <div class="btn__flex">
                                                        <span class="js-input-file__text">Augšuplādēt komandas foto</span>
                                                        <svg class="icon">
                                                            <use
                                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                                xlink:href="/img/icons.svg#arrow--right"></use>
                                                        </svg>
                                                    </div>
                                                </label>
                                                <p class="error hidden  js-input-file__error">Augšuplādējiet bildi kas ir mazāka par <span class="js-allowed-size">NN</span> MB</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--50">
                                            <div class="input-file">
                                                <input
                                                    type="file"
                                                    name="file-2[]"
                                                    id="file-2"
                                                    class="input-file__input  js-input-file"
                                                    data-filesize="8388608"
                                                >
                                                <label
                                                    for="file-2"
                                                    class="layouts-profile-image-input input-file__label btn btn--50 btn--dblue btn--blue-hover btn--blue-active w100  js-input-file__label"
                                                >
                                                    <div class="btn__flex">
                                                        <span class="js-input-file__text">Augšuplādēt krekla foto</span>
                                                        <svg class="icon">
                                                            <use
                                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                                xlink:href="/img/icons.svg#arrow--right"></use>
                                                        </svg>
                                                    </div>
                                                </label>
                                                <p class="error hidden  js-input-file__error">Augšuplādējiet bildi kas ir mazāka par <span class="js-allowed-size">NN</span> MB</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-xl-24">
                                        <div class="w100">
                                            <div class="participant bottom-margin--30 bgc-dgray">
                                                <div class="participant__head bgc-dblue flex wrap--nowrap direction--row justify--start align-items--center c-yellow">
                                                    <div class="participant__number">1.</div>
                                                    <div class="participant__name flex--1">Dalībnieks</div>
                                                    <div class="participant__remove flex wrap--nowrap direction--row justify--center align-items--center">
                                                        <svg class="icon participant__cross">
                                                            <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#cross"></use>
                                                        </svg>
                                                        <div>Noņemt</div>
                                                    </div>
                                                </div>
                                                <div class="participant__form">
                                                    <div class="w100 bottom-margin--20"></div>
                                                    <div class="w100">
                                                        <div class="row row--gutters-50">
                                                            <div class="col-xl-8 col-m-12 col-s-24">
                                                                <div class="input-wrap w100 bottom-margin--15">
                                                                    <label
                                                                        for="input-5"
                                                                        class="input-field-label  js-placeholder"
                                                                    >Vārds *</label>
                                                                    <input
                                                                        type="text"
                                                                        class="input-field if--50 if--dark  js-placeholder-up"
                                                                        id="input-5"
                                                                        name="input-5"
                                                                        data-rule-required="true"
                                                                        data-msg-required="Šis lauks ir aizpildāms obligāti"
                                                                    >
                                                                </div>
                                                            </div>
                                                            <div class="col-xl-8 col-m-12 col-s-24">
                                                                <div class="input-wrap w100 bottom-margin--15">
                                                                    <label
                                                                        for="input-6"
                                                                        class="input-field-label  js-placeholder"
                                                                    >Uzvārds *</label>
                                                                    <input
                                                                        type="text"
                                                                        class="input-field if--50 if--dark  js-placeholder-up"
                                                                        id="input-6"
                                                                        name="input-6"
                                                                        data-rule-required="true"
                                                                        data-msg-required="Šis lauks ir aizpildāms obligāti"
                                                                    >
                                                                </div>
                                                            </div>
                                                            <div class="col-xl-8 col-m-12 col-s-24">
                                                                <div class="input-wrap w100 bottom-margin--20">
                                                                    <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                                                    <select
                                                                        class="select"
                                                                        name="sex"
                                                                        data-rule-required="true"
                                                                        data-msg-required="Lūdzu atzīmējiet savu dzimumu"
                                                                    >
                                                                        <option value="" selected disabled>Dzimums</option>
                                                                        <option value="">1</option>
                                                                        <option value="">2</option>
                                                                        <option value="">3</option>
                                                                    </select>
                                                                </div>
                                                            </div>
                                                            <div class="col-xl-8 col-m-12 col-s-24">
                                                                <div class="input-wrap w100 bottom-margin--20">
                                                                    <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                                                    <select
                                                                        class="select"
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
                                                            </div>
                                                            <div class="col-xl-8 col-m-12 col-s-24">
                                                                <div class="input-wrap w100 bottom-margin--20">
                                                                    <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                                                    <select
                                                                        class="select"
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
                                                            </div>
                                                            <div class="col-xl-8 col-m-12 col-s-24">
                                                                <div class="input-wrap w100 bottom-margin--20">
                                                                    <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                                                    <select
                                                                        class="select"
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
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-xl-24">
                                        <div class="w100 cursor--pointer bottom-margin--30">
                                            <div class="participant__head flex wrap--nowrap direction--row justify--start align-items--center c-yellow">
                                                <div class="participant__number">
                                                    <svg class="icon">
                                                        <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#plus"></use>
                                                    </svg>
                                                </div>
                                                <div class="participant__name flex--1">Pievienot dalībnieku</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-xl-24 border-top">
                                <div class="row">
                                    <div class="col-xl-15 col-m-14 col-s-24"></div>
                                    <div class="col-xl-9 col-m-10 col-s-24">
                                        <button type="submit" class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100">
                                            <div class="btn__flex">
                                                Saglabāt
                                                <svg class="left-margin--15 icon">
                                                    <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#arrow--right"></use>
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
        </div>
    </main>
    <?php include_once('foot.php'); ?>