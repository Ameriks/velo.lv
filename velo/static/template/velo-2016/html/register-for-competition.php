<?php include_once('head.php'); ?>
<main>
    <div class="w100 flex">
        <div class="inner flex">
            <div class="w100 border-right border-left no-border--560">
                <div class="inner no-padding--560">
                    <div class="row">
                        <div class="col-xl-2 col-s-24"></div>
                        <div class="col-xl-20 col-s-24">
                            <h1 class="heading w100 border-right border-left no-border--560 fs30">
                                pieteikties sacensībai
                            </h1>
                            <?php include_once('steps.php'); ?>
                            <form action="" class="w100 js-form-participants">
                                <div class="w100 border-right border-left no-border--560">
                                    <div class="row">
                                        <div class="col-xl-2 col-s-24"></div>
                                        <div class="col-xl-20 col-s-24">
                                            <div class="inner no-padding--560">
                                                <div class="w100 bottom-margin--40"></div>
                                                <div class="w100">
                                                    <div class="row row--gutters-20">
<div class="col-xl-12 col-m-24">
    <div class="input-wrap w100 bottom-margin--15">
        <label
            for="email"
            class="input-field-label  js-placeholder"
        >E-pasts *</label>
        <input
            type="email"
            class="input-field if--50 if--dark  js-placeholder-up"
            id="email"
            name="email"
            data-rule-required="true"
            data-rule-email="true"
            data-msg-required="Šis lauks ir aizpildāms obligāti"
            data-msg-email="Lūdzu ievadiet derīgu e-pasta adresi!"
        >
    </div>
</div>
<div class="col-xl-12 col-m-24">
    <div class="input-wrap w100 bottom-margin--15">
        <label
            for="email_confirm"
            class="input-field-label  js-placeholder"
        >E-pasts atkārtoti *</label>
        <input
            type="email"
            class="input-field if--50 if--dark  js-placeholder-up"
            id="email_confirm"
            name="email_confirm"
            data-rule-required="true"
            data-rule-email="true"
            data-rule-equalto="#email"
            data-msg-required="Šis lauks ir aizpildāms obligāti"
            data-msg-email="Lūdzu ievadiet derīgu e-pasta adresi!"
            data-msg-equalto="E-pasti nesakrīt!"
        >
    </div>
</div>
<div class="col-xl-12 col-m-24">
    <div class="fs13 c-white--50 w100 bottom-margin--15">Uz šo e-pasta adresi tiks sūtīts apmaksas apstiprinājums, kā arī paziņojums par piešķirtajiem starta numuriem.</div>
</div>
<div class="col-xl-12 col-m-24">
    <div class="input-wrap w100 bottom-margin--15">
        <div class="checkbox bottom-margin--15">
            <input class="checkbox__input" type="checkbox" id="checkbox-1" value="" checked="" disabled>
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
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-xl-2 col-s-24"></div>
                                        <div class="layouts-competition-register-background col-xl-24">
                                            <div class="w100">
                                                <div class="inner no-padding--560">
                                                    <div class="row">
                                                        <div class="col-xl-24">
<div class="participant bottom-margin--30 bgc-dgray  js-participant">
    <div class="participant__head bgc-dblue flex wrap--nowrap direction--row justify--start align-items--center c-yellow">
        <div class="participant__number">1.</div>
        <div class="participant__name flex--1">Dalībnieks</div>
        <!-- Pirmajam dalībniekam atšķirībā no pārējiem šeit būs klase .participant__remove--disabled un nebūs klases .js-participant-remove -->
        <div class="participant__remove participant__remove--disabled flex wrap--nowrap direction--row justify--center align-items--center">
            <svg class="icon participant__cross">
                <use
                    xmlns:xlink="http://www.w3.org/1999/xlink"
                    xlink:href="/img/icons.svg#cross"></use>
            </svg>
            <div>Noņemt</div>
        </div>
    </div>
    <div class="participant__form">
        <fieldset class="w100 border-bottom bottom-margin--20">
            <div class="w100 bottom-margin--20"></div>
            <legend class="w100 fs14 fw700 uppercase">Sacensības info</legend>
            <div class="w100">
                <div class="row row--gutters-50">
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--20">
                            <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                            <select
                                class="select"
                                name="competition"
                                id="competition"
                                data-rule-required="true"
                                data-msg-required="Lūdzu izvēlaties kādu no sacensībām"
                                disabled
                            >
                                <option selected disabled>Sacensība</option>
                                <option value="1">1</option>
                                <option value="2">2</option>
                                <option value="3">3</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--20">
                            <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                            <select
                                class="select"
                                name="stage"
                                data-rule-required="true"
                                data-msg-required="Lūdzu izvēlaties kādu no posmiem"
                            >
                                <option value="" selected disabled>Posms</option>
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
                                name="distance"
                                data-rule-required="true"
                                data-msg-required="Lūdzu izvēlaties kādu no distacēm"
                            >
                                <option value="" selected disabled>Distance</option>
                                <option value="">1</option>
                                <option value="">2</option>
                                <option value="">3</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </fieldset>
        <fieldset class="w100 border-bottom bottom-margin--20">
            <legend class="w100 fs14 fw700 uppercase">Dalībnieka info</legend>
            <div class="w100">
                <div class="row row--gutters-50">
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--15">
                            <label
                                for="input-1"
                                class="input-field-label  js-placeholder"
                            >Vārds *</label>
                            <input
                                type="text"
                                class="input-field if--50 if--dark  js-placeholder-up"
                                id="input-1"
                                name="input-1"
                                data-rule-required="true"
                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                disabled
                            >
                        </div>
                    </div>
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--15">
                            <label
                                for="input-2"
                                class="input-field-label  js-placeholder"
                            >Uzvārds *</label>
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
<div class="col-xl-16 col-l-24"> 
    <div class="input-wrap w100 bottom-margin--20">
        <div class="w100 fs13 bottom-margin--10">Dzimšanas datums</div>
        <div class="w100">
            <div class="row row--gutters-20">
                <div class="col-xl-8">
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
                <div class="col-xl-8">
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
                <div class="col-xl-8">
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
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--20">
                            <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                            <select
                                class="select"
                                name="country"
                            >
                                <option value="" selected disabled>Valsts</option>
                                <option value="">1</option>
                                <option value="">2</option>
                                <option value="">3</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--20">
                            <label
                                for="input-3"
                                class="input-field-label  js-placeholder"
                            >Personas kods</label>
                            <input
                                type="text"
                                class="input-field if--50 if--dark  js-placeholder-up"
                                id="input-3"
                                name="input-3"
                                data-rule-minlength="12"
                                data-rule-maxlength="12"
                                data-rule-number="true"
                                data-msg-minlength="Personas kodā ir 11 cipari"
                                data-msg-maxlength="Personas kodā ir 11 cipari"
                                data-msg-number="Lūdzu ievadiet tikai ciparus"
                            >
                        </div>
                    </div>
                    <div class="col-xl-8 col-m-12 col-s-24"></div>
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--20">
                            <label
                                for="input-6"
                                class="input-field-label  js-placeholder"
                            >E-pasts</label>
                            <input
                                type="email"
                                class="input-field if--50 if--dark  js-placeholder-up"
                                id="input-6"
                                name="input-6"
                                data-rule-email="true"
                                data-msg-email="Lūdzu ievadiet derīgu e-pasta adresi!"
                            >
                        </div>
                    </div>
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--20">
                            <label
                                for="input-4"
                                class="input-field-label  js-placeholder"
                            >Telefona numurs</label>
                            <input
                                type="text"
                                class="input-field if--50 if--dark  js-placeholder-up"
                                id="input-4"
                                name="input-4"
                                data-rule-number="true"
                                data-msg-number="Lūdzu ievadiet tikai ciparus"
                            >
                        </div>
                    </div>
                </div>
            </div>
        </fieldset>
        <fieldset class="w100">
            <legend class="w100 fs14 fw700 uppercase">Sacensības info</legend>
            <div class="w100">
                <div class="row row--gutters-50">
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--15">
                            <label
                                for="input-5"
                                class="input-field-label  js-placeholder"
                            >Komanda</label>
                            <input
                                type="text"
                                class="input-field if--50 if--dark  js-placeholder-up"
                                id="input-5"
                                name="input-5"
                            >
                        </div>
                    </div>
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--15">
                            <label
                                for="input-7"
                                class="input-field-label  js-placeholder"
                            >Velo marka</label>
                            <input
                                type="text"
                                class="input-field if--50 if--dark  js-placeholder-up"
                                id="input-7"
                                name="input-7"
                            >
                        </div>
                    </div>
                    <div class="col-xl-8 col-m-12 col-s-24">
                        <div class="input-wrap w100 bottom-margin--20">
                            <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                            <select
                                class="select"
                                name="insurance"
                            >
                                <option value="" selected disabled>Apdrošināšana</option>
                                <option value="">1</option>
                                <option value="">2</option>
                                <option value="">3</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-xl-24">
                        <div class="fs12 fw700 c-white--70 uppercase text-align--right bottom-margin--10">DALĪBAS MAKSA - <span class="c-yellow--70">19EUR</span></div>
                        <div class="fs12 fw700 c-white--70 uppercase text-align--right bottom-margin--10">2. Līnija - <span class="c-yellow--70">191EUR</span></div>
                        <div class="fs14 fw700 c-white uppercase text-align--right">3. Līnija - <span class="c-yellow">191EUR</span></div>
                    </div>
                </div>
            </div>
        </fieldset>
    </div>
</div>

<div class="w100 js-participant-load-area">
    <div class="participant bottom-margin--30 bgc-dgray  js-participant">
        <div class="participant__head bgc-dblue flex wrap--nowrap direction--row justify--start align-items--center c-yellow">
            <div class="participant__number">2.</div>
            <div class="participant__name flex--1">Dalībnieks</div>
            <div class="participant__remove flex wrap--nowrap direction--row justify--center align-items--center  js-participant-remove">
                <svg class="icon participant__cross">
                    <use
                        xmlns:xlink="http://www.w3.org/1999/xlink"
                        xlink:href="/img/icons.svg#cross"></use>
                </svg>
                <div>Noņemt</div>
            </div>
        </div>
        <div class="participant__form">
            <fieldset class="w100 border-bottom bottom-margin--20">
                <div class="w100 bottom-margin--20"></div>
                <legend class="w100 fs14 fw700 uppercase">Sacensības info</legend>
                <div class="w100">
                    <div class="row row--gutters-50">
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--20">
                                <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                <select
                                    class="select"
                                    name="competition"
                                    id="competition"
                                    data-rule-required="true"
                                    data-msg-required="Lūdzu izvēlaties kādu no sacensībām"
                                >
                                    <option selected disabled>Sacensība</option>
                                    <option value="1">1</option>
                                    <option value="2">2</option>
                                    <option value="3">3</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--20">
                                <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                <select
                                    class="select"
                                    name="stage"
                                    data-rule-required="true"
                                    data-msg-required="Lūdzu izvēlaties kādu no posmiem"
                                >
                                    <option value="" selected disabled>Posms</option>
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
                                    name="distance"
                                    data-rule-required="true"
                                    data-msg-required="Lūdzu izvēlaties kādu no distacēm"
                                >
                                    <option value="" selected disabled>Distance</option>
                                    <option value="">1</option>
                                    <option value="">2</option>
                                    <option value="">3</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </fieldset>
            <fieldset class="w100 border-bottom bottom-margin--20">
                <legend class="w100 fs14 fw700 uppercase">Dalībnieka info</legend>
                <div class="w100">
                    <div class="row row--gutters-50">
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--15">
                                <label
                                    for="input-1"
                                    class="input-field-label  js-placeholder"
                                >Vārds *</label>
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
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--15">
                                <label
                                    for="input-2"
                                    class="input-field-label  js-placeholder"
                                >Uzvārds *</label>
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
                                    name="country"
                                >
                                    <option value="" selected disabled>Valsts</option>
                                    <option value="">1</option>
                                    <option value="">2</option>
                                    <option value="">3</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--20">
                                <label
                                    for="input-3"
                                    class="input-field-label  js-placeholder"
                                >Personas kods</label>
                                <input
                                    type="text"
                                    class="input-field if--50 if--dark  js-placeholder-up"
                                    id="input-3"
                                    name="input-3"
                                    data-rule-minlength="12"
                                    data-rule-maxlength="12"
                                    data-rule-number="true"
                                    data-msg-minlength="Personas kodā ir 11 cipari"
                                    data-msg-maxlength="Personas kodā ir 11 cipari"
                                    data-msg-number="Lūdzu ievadiet tikai ciparus"
                                >
                            </div>
                        </div>
                        <div class="col-xl-8 col-m-12 col-s-24"></div>
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--20">
                                <label
                                    for="input-6"
                                    class="input-field-label  js-placeholder"
                                >E-pasts</label>
                                <input
                                    type="email"
                                    class="input-field if--50 if--dark  js-placeholder-up"
                                    id="input-6"
                                    name="input-6"
                                    data-rule-email="true"
                                    data-msg-email="Lūdzu ievadiet derīgu e-pasta adresi!"
                                >
                            </div>
                        </div>
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--20">
                                <label
                                    for="input-4"
                                    class="input-field-label  js-placeholder"
                                >Telefona numurs</label>
                                <input
                                    type="text"
                                    class="input-field if--50 if--dark  js-placeholder-up"
                                    id="input-4"
                                    name="input-4"
                                    data-rule-number="true"
                                    data-msg-number="Lūdzu ievadiet tikai ciparus"
                                >
                            </div>
                        </div>
                    </div>
                </div>
            </fieldset>
            <fieldset class="w100">
                <legend class="w100 fs14 fw700 uppercase">Sacensības info</legend>
                <div class="w100">
                    <div class="row row--gutters-50">
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--15">
                                <label
                                    for="input-5"
                                    class="input-field-label  js-placeholder"
                                >Komanda</label>
                                <input
                                    type="text"
                                    class="input-field if--50 if--dark  js-placeholder-up"
                                    id="input-5"
                                    name="input-5"
                                >
                            </div>
                        </div>
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--15">
                                <label
                                    for="input-7"
                                    class="input-field-label  js-placeholder"
                                >Velo marka</label>
                                <input
                                    type="text"
                                    class="input-field if--50 if--dark  js-placeholder-up"
                                    id="input-7"
                                    name="input-7"
                                >
                            </div>
                        </div>
                        <div class="col-xl-8 col-m-12 col-s-24">
                            <div class="input-wrap w100 bottom-margin--20">
                                <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                <select
                                    class="select"
                                    name="insurance"
                                >
                                    <option value="" selected disabled>Apdrošināšana</option>
                                    <option value="">1</option>
                                    <option value="">2</option>
                                    <option value="">3</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-xl-24">
                            <div class="fs14 fw700 c-white uppercase text-align--right">DALĪBAS MAKSA - <span class="c-yellow">19EUR</span></div>
                        </div>
                    </div>
                </div>
            </fieldset>
        </div>
    </div>
</div>

<div class="w100 cursor--pointer bottom-margin--30  js-add-participant">
    <div class="participant__head flex wrap--nowrap direction--row justify--start align-items--center c-yellow">
        <div class="participant__number">
            <svg class="icon">
                <use
                    xmlns:xlink="http://www.w3.org/1999/xlink"
                    xlink:href="/img/icons.svg#plus"></use>
            </svg>
        </div>
        <div class="participant__name flex--1">Pievienot dalībnieku</div>
    </div>
</div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="layouts-competition-register-background col-xl-24 border-top">
                                            <div class="inner">
                                                <div class="row">
                                                    <div class="col-xl-24">
                                                        <div class="w100 bottom-margin--20"></div>
                                                        <div class="w100">
                                                            <div class="row">
                                                                <div class="col-xs-24 flex--1 fs14 fw700 uppercase bottom-margin--20  js-paricipant-count">2 DALĪBAS PIETEIKUMI </div>
                                                                <div class="col-xs-24 fs14 fw700 uppercase bottom-margin--20">kopā - <span class="c-yellow">38EUR</span></div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-xl-24 border-top border-bottom">
                                            <div class="row">
                                                <div class="col-xl-15 col-m-14 col-s-24"></div>
                                                <div class="col-xl-9 col-m-10 col-s-24">
                                                    <button type="submit" class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100">
                                                        <div class="btn__flex">
                                                            Tālāk
                                                            <svg class="left-margin--15 icon">
                                                                <use
                                                                    xmlns:xlink="http://www.w3.org/1999/xlink"
                                                                    xlink:href="/img/icons.svg#arrow--right"></use>
                                                            </svg>
                                                        </div>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-xl-24">
                                            <div class="w100 bottom-margin--20"></div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>