<?php include_once('head.php'); ?>
<main>
    <div class="w100">
        <div class="inner">
            <div class="w100 border-right border-left no-border--480 bottom-padding--80">
                <div class="inner no-padding--480">
                    <div class="row">
                        <div class="col-xl-5 col-l-24"></div>
                        <div class="col-xl-14 col-l-24">
                            <div class="w100 bottom-margin--50"></div>
                            <h1 class="ti fs30 fw700 uppercase w100 bottom-margin--15">Reģistrācija</h1>
                            <form action="" class="w100 js-form">
                                <div class="row row--gutters-20">
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--15">
                                            <label
                                                for="input-1"
                                                class="input-field-label  js-placeholder"
                                            >E-pasts *</label>
                                            <input
                                                type="email"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-1"
                                                name="input-1"
                                                data-rule-required="true"
                                                data-rule-email="true"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                                data-msg-email="Lūdzu ievadiet derīgu e-pasta adresi!"
                                            >
                                        </div>
                                    </div>
                                </div>
                                <div class="row row--gutters-20">
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--15">
                                            <label
                                                for="password"
                                                class="input-field-label  js-placeholder"
                                            >Parole *</label>
                                            <input
                                                type="password"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="password"
                                                name="password"
                                                data-rule-required="true"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--15">
                                            <label
                                                for="password_confirm"
                                                class="input-field-label  js-placeholder"
                                            >Parole atkārtoti *</label>
                                            <input
                                                type="password"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="password_confirm"
                                                name="password_confirm"
                                                data-rule-required="true"
                                                data-rule-equalto="#password"
                                                data-msg-required="Šis lauks ir aizpildāms obligāti"
                                                data-msg-equalto="Paroles nesakrīt!"
                                            >
                                        </div>
                                    </div>
                                </div>
                                <div class="row row--gutters-20">
                                    <div class="col-xl-24">
                                        <div class="input-wrap w100 bottom-margin--15">
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
                                <div class="row">
                                    <div class="col-xl-24 border-top bottom-margin--15"></div>
                                </div>
                                <div class="row row--gutters-20">
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--15">
                                            <label
                                                for="input-2"
                                                class="input-field-label  js-placeholder"
                                            >Vārds</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-2"
                                                name="input-2"
                                            >
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--15">
                                            <label
                                                for="input-3"
                                                class="input-field-label  js-placeholder"
                                            >Uzvārds</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-3"
                                                name="input-3"
                                            >
                                        </div>
                                    </div>
                                </div>
                                <div class="row row--gutters-20">
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <label for="input-4" class="w100 fs13 bottom-margin--10">Dzimšanas diena</label>
                                            <div class="w100">
                                                <div class="row row--gutters-20">
                                                    <div class="col-xl-8">
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark if--center  js-placeholder-up"
                                                            id="input-4"
                                                            name="input-4"
                                                            placeholder="DD"
                                                            data-rule-maxlength="2"
                                                            data-rule-range="1,31"
                                                            data-msg-maxlength="Lūdzu ievadiet pareizu dienas skaitli"
                                                            data-msg-range="Lūdzu ievadiet pareizu dienas skaitli"
                                                        >
                                                    </div>
                                                    <div class="col-xl-8">
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark if--center  js-placeholder-up"
                                                            id="input-5"
                                                            name="input-5"
                                                            placeholder="MM"
                                                            data-rule-maxlength="2"
                                                            data-rule-range="1,12"
                                                            data-msg-maxlength="Lūdzu ievadiet pareizu mēneša skaitli"
                                                            data-msg-range="Lūdzu ievadiet pareizu mēneša skaitli"
                                                        >
                                                    </div>
                                                    <div class="col-xl-8">
                                                        <input
                                                            type="text"
                                                            class="input-field if--50 if--dark if--center  js-placeholder-up"
                                                            id="input-6"
                                                            name="input-6"
                                                            placeholder="GGGG"
                                                            data-rule-minlength="4"
                                                            data-rule-maxlength="4"
                                                            data-msg-minlength="Lūdzu ievadiet pareizu gada skaitli"
                                                            data-msg-maxlength="Lūdzu ievadiet pareizu gada skaitli"
                                                        >
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row row--gutters-20">
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <select
                                                class="select"
                                                name="country"
                                            >
                                                <option value="" selected disabled>Valsts</option>
                                                <option value="">Igaunija</option>
                                                <option value="">Latvija</option>
                                                <option value="">Lietuva</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--20">
                                            <select
                                                class="select"
                                                name="city"
                                            >
                                                <option value="" selected disabled>Pilsēta</option>
                                                <option value="">Rīga</option>
                                                <option value="">Liepāja</option>
                                                <option value="">Daugavpils</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--15">
                                            <select
                                                class="select"
                                                name="velo"
                                            >
                                                <option value="" selected disabled>Velo marka</option>
                                                <option value="">Trek</option>
                                                <option value="">Rockmachine</option>
                                                <option value="">Miranda</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row row--gutters-20">
                                    <div class="col-xl-12 col-s-24">
                                        <div class="input-wrap w100 bottom-margin--30">
                                            <label
                                                for="input-7"
                                                class="input-field-label  js-placeholder"
                                            >Telefona numurs</label>
                                            <input
                                                type="text"
                                                class="input-field if--50 if--dark  js-placeholder-up"
                                                id="input-7"
                                                name="input-7"
                                                data-rule-number="true"
                                                data-msg-number="Lūdzu ievadiet tikai ciparus"
                                            >
                                        </div>
                                    </div>
                                </div>
                                <div class="row row--gutters-20">
                                    <div class="col-xl-12 col-s-24">
                                        <button class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100">
                                            <div class="btn__flex">
                                                Reģistrēties
                                                <svg class="icon">
                                                    <use
                                                        xmlns:xlink="http://www.w3.org/1999/xlink"
                                                        xlink:href="/img/icons.svg#arrow--right"></use>
                                                </svg>
                                            </div>
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="col-xl-5 col-l-24"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>