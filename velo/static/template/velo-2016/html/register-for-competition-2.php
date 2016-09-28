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
                            <form action="" class="w100 border-right border-left no-border--560 bgc-dgray  js-form">
                                <div class="w100 bottom-margin--20"></div>
                                <div class="inner no-padding--560">
                                    <div class="w100 overflow--auto bottom-margin--20">
                                        <table class="table-block table-block--thead-border">
                                            <thead>
                                                <tr>
                                                    <th>#</th>
                                                    <th>Vārds UZvārds</th>
                                                    <th>DZIMŠANAS DIENA</th>
                                                    <th>KOMANDA</th>
                                                    <th>Cena</th>
                                                    <th>Apdrosināšana</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr>
                                                    <td>1</td>
                                                    <td>Raivis Belahoščiks</td>
                                                    <td>05.03.1970.</td>
                                                    <td>Apvienotā Zolitūdes velo komanda</td>
                                                    <td>19 €</td>
                                                    <td>-</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                    <a href="" class="w100 bottom-margin--30">
                                        <div class="participant__head flex wrap--nowrap direction--row justify--start align-items--center c-yellow">
                                            <div class="participant__number">
                                                <svg class="icon">
                                                    <use
                                                        xmlns:xlink="http://www.w3.org/1999/xlink"
                                                        xlink:href="/img/icons.svg#plus"></use>
                                                </svg>
                                            </div>
                                            <div class="participant__name flex--1">Pievienot / labot dalībniekus</div>
                                        </div>
                                    </a>
                                    <div class="input-wrap w100 bottom-margin--20">
                                        <div class="checkbox">
                                            <input
                                                class="checkbox__input"
                                                type="checkbox"
                                                name="checkbox-1"
                                                id="checkbox-1"
                                                value=""
                                                data-rule-required="true"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                            >
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
                                                    <span class="checkbox__text">Apliecinu, ka mans veselības stāvoklis atļauj startēt izvēlētajā distancē. Apņemos ievērot ceļu satiksmes noteikumus un sacensību nolikumu,
kā arī obligāti lietot aizsprādzētu aizsargķiveri visos sacensību posmos.</span>
                                                </div>
                                            </label>
                                        </div>
                                    </div>
                                    <div class="input-wrap w100 bottom-margin--20">
                                        <div class="checkbox">
                                            <input
                                                class="checkbox__input"
                                                type="checkbox"
                                                name="checkbox-2"
                                                id="checkbox-2"
                                                value=""
                                                data-rule-required="true"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                            >
                                            <label for="checkbox-2" class="checkbox__label">
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
                                                    <span class="checkbox__text">Apliecinu, ka informēšu pieteiktos dalībniekus par noteikumiem.</span>
                                                </div>
                                            </label>
                                        </div>
                                    </div>
                                    
                                    <div class="input-wrap w100 bottom-margin--20">
                                        <div class="row row--gutters-10">
                                            <div class="col-xl-4 col-l-5 col-m-8 col-xs-12">
                                                <div class="w100 bottom-margin--15">
                                                    <div class="input-filed-with-select  js-input-field-with-select">
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark input-filed-with-select__field  js-input-field-with-select__field"
                                                            placeholder="€ 0"
                                                        >
                                                        <select
                                                            class="select input-filed-with-select__select  js-input-field-with-select__select"
                                                            name="charity"
                                                            id="charity"
                                                        >
                                                            <option selected disabled>€ 0</option>
                                                            <option value="5">€ 5</option>
                                                            <option value="10">€ 10</option>
                                                            <option value="15">€ 15</option>
                                                        </select>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-xl-20 col-l-19 col-m-16 col-s-24">
                                                <p><span class="fw700">Ziedot SOS Bērnu ciematu jauniešu interešu izglītībai:</span><br>
                                                Aicinām sniegt finansiālu atbalstu, lai nodrošinātu sportošanas un izglītības nodarbības bez vecāku gādības palikušajiem Latvijas SOS bērnu ciematu asociācijas jauniešiem.</p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="layouts-competition-register-total w100 bgc-dblue bottom-margin--20">
                                        <div class="inner">
                                            <div class="w100 bottom-margin--20"></div>
                                            <div class="w100">
                                                <div class="row">
                                                    <div class="col-xs-24 flex--1 fs14 fw700 uppercase bottom-margin--20  js-paricipant count">2 DALĪBAS PIETEIKUMI </div>
                                                    <div class="col-xs-24 fs14 fw700 uppercase bottom-margin--20">kopā - <span class="c-yellow">38EUR</span></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                </div>
                                <div class="w100 border-top">
                                    <div class="w100 bottom-margin--30"></div>
                                    <div class="inner no-padding--560">
                                        <div class="fs14 fw700 uppercase w100 bottom-margin--30">MAKSāšanas VEIDS</div>
                                        <div class="input-wrap w100">
                                            <div class="w100">
                                                <div class="row row--gutters-20">
                                                    <div class="col-xl-6 col-l-12 col-xs-24">
                                                        <div class="w100 bottom-margin--20">
                                                            <div class="check-button w100">
                                                                <input
                                                                    class="check-button__input"
                                                                    type="radio"
                                                                    name="payment"
                                                                    value="1"
                                                                    id="radio-1"
                                                                    data-rule-required="true"
                                                                    data-msg-required="Izvēlies kādu no maksāšanas veidiem"
                                                                >
                                                                <label for="radio-1" class="check-button__label flex direction--row justify--center align-items--center">
                                                                    <span class="fw700 fs14 uppercase">SAŅEMT ŖĒĶINU</span>
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div class="col-xl-6 col-l-12 col-xs-24">
                                                        <div class="w100 bottom-margin--20">
                                                            <div class="check-button w100">
                                                                <input
                                                                    class="check-button__input"
                                                                    type="radio"
                                                                    name="payment"
                                                                    value="2"
                                                                    id="radio-2"
                                                                    data-rule-required="true"
                                                                    data-msg-required="Izvēlies kādu no maksāšanas veidiem"
                                                                >
                                                                <label for="radio-2" class="check-button__label  flex direction--row justify--center align-items--center">
                                                                    <figure class="check-button__image img-wrapper">
                                                                        <img
                                                                            data-src="/img/logos/swedbank.png"
                                                                            onload="imgLoaded(this)"
                                                                        >
                                                                    </figure>
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div class="col-xl-6 col-l-12 col-xs-24">
                                                        <div class="w100 bottom-margin--20">
                                                            <div class="check-button w100">
                                                                <input
                                                                    class="check-button__input"
                                                                    type="radio"
                                                                    name="payment"
                                                                    value="3"
                                                                    id="radio-3"
                                                                    data-rule-required="true"
                                                                    data-msg-required="Šis lauks ir aizpildāms obligāti"
                                                                >
                                                                <label for="radio-3" class="check-button__label  flex direction--row justify--center align-items--center">
                                                                    <figure class="check-button__image img-wrapper">
                                                                        <img
                                                                            data-src="/img/logos/ibanka.png"
                                                                            onload="imgLoaded(this)"
                                                                        >
                                                                    </figure>
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div class="col-xl-6 col-l-12 col-xs-24">
                                                        <div class="w100 bottom-margin--20">
                                                            <div class="check-button w100">
                                                                <input
                                                                    class="check-button__input"
                                                                    type="radio"
                                                                    name="payment"
                                                                    value="4"
                                                                    id="radio-4"
                                                                    data-rule-required="true"
                                                                    data-msg-required="Šis lauks ir aizpildāms obligāti"
                                                                >
                                                                <label for="radio-4" class="check-button__label  flex direction--row justify--center align-items--center">
                                                                    <figure class="check-button__image img-wrapper">
                                                                        <img
                                                                            data-src="/img/logos/visa_maestro_mastercard.svg"
                                                                            onload="imgLoaded(this)"
                                                                        >
                                                                    </figure>
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="w100">
                                        <div class="inner no-padding--560">
                                            <div class="row row--gutters-50">
                                                <div class="col-xl-8 col-l-12 col-m-24">
                                                    <div class="input-wrap w100 bottom-margin--15">
                                                        <label
                                                            for="input-1"
                                                            class="input-field-label  js-placeholder"
                                                        >Company name / full name</label>
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark  js-placeholder-up"
                                                            id="input-1"
                                                            name="input-1"
                                                        >
                                                    </div>
                                                </div>
                                                <div class="col-xl-8 col-l-12 col-m-24">
                                                    <div class="input-wrap w100 bottom-margin--15">
                                                        <label
                                                            for="input-2"
                                                            class="input-field-label  js-placeholder"
                                                        >VAT number</label>
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark  js-placeholder-up"
                                                            id="input-2"
                                                            name="input-2"
                                                        >
                                                    </div>
                                                </div>
                                                <div class="col-xl-8 col-l-12 col-m-24">
                                                    <div class="input-wrap w100 bottom-margin--15">
                                                        <label
                                                            for="input-3"
                                                            class="input-field-label  js-placeholder"
                                                        >Company number / SSN</label>
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark  js-placeholder-up"
                                                            id="input-3"
                                                            name="input-3"
                                                        >
                                                    </div>
                                                </div>
                                                <div class="col-xl-8 col-l-12 col-m-24">
                                                    <div class="input-wrap w100 bottom-margin--15">
                                                        <label
                                                            for="input-4"
                                                            class="input-field-label  js-placeholder"
                                                        >Address</label>
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark  js-placeholder-up"
                                                            id="input-4"
                                                            name="input-4"
                                                        >
                                                    </div>
                                                </div>
                                                <div class="col-xl-8 col-l-12 col-m-24">
                                                    <div class="input-wrap w100 bottom-margin--15">
                                                        <label
                                                            for="input-5"
                                                            class="input-field-label  js-placeholder"
                                                        >Juridical address</label>
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark  js-placeholder-up"
                                                            id="input-5"
                                                            name="input-5"
                                                        >
                                                    </div>
                                                </div>
                                                <div class="col-xl-24">
                                                    <div class="w100 fs13 bottom-margin--10">&nbsp;</div>
                                                    <div class="input-wrap w100 bottom-margin--20">
                                                        <div class="checkbox">
                                                            <input class="checkbox__input" type="checkbox" name="checkbox-3" id="checkbox-3" value="" data-rule-required="true" data-msg-required="Šis lauks ir aizpildāms obligāti" aria-required="true">
                                                            <label for="checkbox-3" class="checkbox__label">
                                                                <div class="flex wrap--nowrap direction--row justify--start align-items--center">
                                                                    <svg class="checkbox__graphic checkbox__graphic--default icon">
                                                                        <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#checkbox--default"></use>
                                                                    </svg>
                                                                    <svg class="checkbox__graphic checkbox__graphic--checked icon">
                                                                        <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#checkbox--checked"></use>
                                                                    </svg>
                                                                    <span class="checkbox__text">Show participant names in invoice</span>
                                                                </div>
                                                            </label>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="w100 bottom-margin--10"></div>
                                </div>
                                <div class="w100 border-top border-bottom">
                                    <div class="row">
                                        <div class="col-xl-15 col-m-14 col-s-24"></div>
                                        <div class="col-xl-9 col-m-10 col-s-24">
                                            <button type="submit" class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100">
                                                <div class="btn__flex">
                                                    Maksāt
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
                                <div class="w100 bottom-margin--20"></div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>