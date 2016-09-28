<?php include_once('head.php'); ?>
<main>
    <div class="w100 flex">
        <div class="inner flex">
            <div class="w100 border-right border-left no-border--480 bottom-padding--80">
                <div class="inner no-padding--480">
                    <div class="row">
                        <div class="col-xl-4 col-l-24"></div>
                        <div class="col-xl-16 col-l-24">
                            <div class="w100 bottom-margin--50"></div>
                            <h1 class="ti fs30 fw700 uppercase w100 bottom-margin--40">Ienākt</h1>
                            <div class="w100">
                                <div class="row">
                                    <div class="col-xl-12 col-m-24 layouts-login-left">
                                        <form action="" class="w100  js-form">
                                            <div class="input-wrap w100 bottom-margin--10">
                                                <input
                                                    type="text"
                                                    class="input-field if--50 if--dark"
                                                    id="input-1"
                                                    name="input-1"
                                                    placeholder="E-pasts"
                                                    data-rule-required="true"
                                                    data-rule-email="true"
                                                    data-msg-required="Šis lauks ir aizpildāms obligāti"
                                                    data-msg-email="Lūdzu ievadiet derīgu e-pasta adresi!"
                                                >
                                            </div>
                                            <div class="input-wrap w100 bottom-margin--10">
                                                <input
                                                    type="password"
                                                    class="input-field if--50 if--dark"
                                                    id="password"
                                                    name="password"
                                                    placeholder="Parole"
                                                    data-rule-required="true"
                                                    data-msg-required="Šis lauks ir aizpildāms obligāti"
                                                >
                                            </div>
                                            <button class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100 bottom-margin--10">
                                                <div class="btn__flex">
                                                    Ienākt
                                                    <svg class="icon">
                                                        <use
                                                            xmlns:xlink="http://www.w3.org/1999/xlink"
                                                            xlink:href="/img/icons.svg#arrow--right"></use>
                                                    </svg>
                                                </div>
                                            </button>
                                        </form>
                                        <div class="w100 text-align--right">
                                            <a href="" class="ti fs13 underline c-white--50">Aizmirsāt paroli?</a>
                                        </div>
                                    </div>
                                    <div class="col-xl-12 col-m-24">
                                        <div class="w100 layouts-login-right">
                                            <a href="" class="btn btn--50 btn--yellow-transparent btn--blue-hover btn--blue-active w100 bottom-margin--10">
                                                <div class="btn__flex">
                                                    Reģistrēties
                                                    <svg class="icon">
                                                        <use
                                                            xmlns:xlink="http://www.w3.org/1999/xlink"
                                                            xlink:href="/img/icons.svg#arrow--right"></use>
                                                    </svg>
                                                </div>
                                            </a>
                                            <a href="" class="btn btn--50 btn--twitter btn--no-padding btn--no-borders w100 bottom-margin--10">
                                                <div class="w100 flex wrap--nowrap direction--row justify--start align-items--center">
                                                    <span class="btn__icon-block">
                                                        <svg class="btn__icon-block-icon icon">
                                                            <use
                                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                                xlink:href="/img/icons.svg#twitter"></use>
                                                        </svg>
                                                    </span>
                                                    <span class="left-margin--20 no-wrap">IENĀKT ar twitter</span>
                                                </div>
                                            </a>
                                            <a href="" class="btn btn--50 btn--facebook btn--no-padding btn--no-borders w100 bottom-margin--10">
                                                <div class="w100 flex wrap--nowrap direction--row justify--start align-items--center">
                                                    <span class="btn__icon-block">
                                                        <svg class="btn__icon-block-icon icon">
                                                            <use
                                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                                xlink:href="/img/icons.svg#facebook"></use>
                                                        </svg>
                                                    </span>
                                                    <span class="left-margin--20 no-wrap">IENĀKT ar facebook</span>
                                                </div>
                                            </a>
                                            <a href="" class="btn btn--50 btn--draugiem btn--no-padding btn--no-borders w100">
                                                <div class="w100 flex wrap--nowrap direction--row justify--start align-items--center">
                                                    <span class="btn__icon-block">
                                                        <svg class="btn__icon-block-icon icon">
                                                            <use
                                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                                xlink:href="/img/icons.svg#draugiem"></use>
                                                        </svg>
                                                    </span>
                                                    <span class="left-margin--20 no-wrap">IENĀKT ar draugiem pasi</span>
                                                </div>
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-xl-4 col-l-24"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>