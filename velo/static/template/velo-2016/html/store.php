<?php include_once('head.php'); ?>
<main>
    <div class="inner flex">
        <div class="w100 flex--1">
            <div class="row">
                <div class="col-xl-17 col-l-15 col-m-14 col-s-24 border-right border-left no-border--560 flex direction--column justify--start align-items--start">
                    <h1 class="primary-heading c-white border-bottom">
                        <div class="primary-heading__spacing w100">
                            <h1 class="primary-heading__text primary-heading__text--smaller flex justify-start align-items--center">PRODUKTA NOSAUKUMS</h1>
                        </div>
                    </h1>
                    <div class="layouts-store-left bgc-dblue w100 flex--1">
                        <article class="article flex--1">
                            <figure class="article__image img-wrapper">
                                <img onload="imgLoaded(this)" src="/userfiles/article-img.jpg">
                            </figure>
                            <div class="article__text editor-text">
                                <h3><strong>Projekts 05.02.2016.</strong></h3><h2>1. Vispārējie noteikumi</h2><h3>1.1 Mērķi</h3><ul><li>Veicināt un popularizēt MTB sportu Latvijā kā visiem pieejamu sporta veidu.</li><li>Veicināt cilvēku regulāru nodarbošanos ar fiziskām aktivitātēm brīvā dabā.</li><li>Audzināt cilvēkos saudzējošu attieksmi pret dabu un popularizēt tīru vidi Latvijas dabā.</li><li>Noskaidrot labākos Latvijas MTB maratona braucējus dažādās vecuma grupās.</li></ul><h3>1.2 Sacensību kalendārs</h3>
                            </div>
                        </article>
                    </div>
                </div>
                <div class="col-xl-7 col-l-9 col-m-10 col-s-24 border-right no-border--560 flex direction--column justify--start align-items--start">
                    <h2 class="primary-heading c-white border-bottom">
                        <div class="primary-heading__spacing w100">
                            <h1 class="primary-heading__text primary-heading__text--smaller flex justify-start align-items--center">Pirkuma DETAĻAS</h1>
                        </div>
                    </h2>
                    <form action="" class="layouts-store-right bgc-dblue flex--1  js-form">
                        <div class="layouts-store-toolbox border-bottom">
                            <p class="w100 fs13 bottom-margin--10">Izmērs</p>
                            <div class="layouts-store-toolbox-grid input-wrap">
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="size"
                                        value="1"
                                        id="size-1"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies izmēru"
                                    >
                                    <label for="size-1" class="store-button__label flex direction--row justify--center align-items--center">
                                        <span class="fw700 fs14 uppercase">XS</span>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="size"
                                        value="2"
                                        id="size-2"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies izmēru"
                                    >
                                    <label for="size-2" class="store-button__label flex direction--row justify--center align-items--center">
                                        <span class="fw700 fs14 uppercase">S</span>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="size"
                                        value="3"
                                        id="size-3"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies izmēru"
                                    >
                                    <label for="size-3" class="store-button__label flex direction--row justify--center align-items--center">
                                        <span class="fw700 fs14 uppercase">M</span>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="size"
                                        value="4"
                                        id="size-4"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies izmēru"
                                    >
                                    <label for="size-4" class="store-button__label flex direction--row justify--center align-items--center">
                                        <span class="fw700 fs14 uppercase">L</span>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="size"
                                        value="5"
                                        id="size-5"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies izmēru"
                                    >
                                    <label for="size-5" class="store-button__label flex direction--row justify--center align-items--center">
                                        <span class="fw700 fs14 uppercase">XL</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="layouts-store-toolbox border-bottom">
                            <p class="w100 fs13 bottom-margin--10">Krāsa</p>
                            <div class="layouts-store-toolbox-grid input-wrap">
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="color"
                                        value="1"
                                        id="color-1"
                                        checked
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies krāsu"
                                    >
                                    <label for="color-1" class="store-button__label flex direction--row justify--center align-items--center">
                                        <div class="store-button__color" style="background-color:#be1e2d;"></div>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="color"
                                        value="2"
                                        id="color-2"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies krāsu"
                                    >
                                    <label for="color-2" class="store-button__label flex direction--row justify--center align-items--center">
                                        <div class="store-button__color" style="background-color:#92278f;"></div>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="color"
                                        value="3"
                                        id="color-3"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies krāsu"
                                    >
                                    <label for="color-3" class="store-button__label flex direction--row justify--center align-items--center">
                                        <div class="store-button__color" style="background-color:#f7941e;"></div>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="color"
                                        value="4"
                                        id="color-4"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies krāsu"
                                    >
                                    <label for="color-4" class="store-button__label flex direction--row justify--center align-items--center">
                                        <div class="store-button__color" style="background-color:#8dc63f;"></div>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="color"
                                        value="5"
                                        id="color-5"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies krāsu"
                                    >
                                    <label for="color-5" class="store-button__label flex direction--row justify--center align-items--center">
                                        <div class="store-button__color" style="background-color:#f9ed32;"></div>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="color"
                                        value="6"
                                        id="color-6"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies krāsu"
                                    >
                                    <label for="color-6" class="store-button__label flex direction--row justify--center align-items--center">
                                        <div class="store-button__color" style="background-color:#a97c50;"></div>
                                    </label>
                                </div>
                                <div class="store-button">
                                    <input
                                        class="store-button__input"
                                        type="radio"
                                        name="color"
                                        value="7"
                                        id="color-7"
                                        data-rule-required="true"
                                        data-msg-required="Izvēlies kādu no maksāšanas veidiem"
                                    >
                                    <label for="color-7" class="store-button__label flex direction--row justify--center align-items--center">
                                        <div class="store-button__color" style="background-color:#2b3990;"></div>
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="layouts-store-toolbox border-bottom">
                            <p class="w100 fs13 bottom-margin--15">Skaits</p>
                            <div class="input-amount js-input-amount">
                                <input
                                    type="text"
                                    name="amount"
                                    readonly="readonly"
                                    class="input-amount__value  js-input-amount-value"
                                    value="1"
                                >
                                <div class="input-amount__buttons">
                                    <div class="input-amount__btn input-amount__btn--plus  js-input-amount-plus">
                                        <svg class="input-amount__icon icon">
                                            <use
                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                xlink:href="/img/icons.svg#plus"></use>
                                        </svg>
                                    </div>
                                    <div class="input-amount__btn input-amount__btn--minus  js-input-amount-minus">
                                        <svg class="input-amount__icon icon">
                                            <use
                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                xlink:href="/img/icons.svg#minus"></use>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="layouts-store-toolbox">
                            <label for="comment" class="w100 fs13 bottom-margin--15">Komentāri</label>
                            <textarea
                                name="comment"
                                id="comment"
                                class="layouts-store-textarea input-field if--50 if--dark input-field--textarea"
                                placeholder="Piebilde par produktu, izmēra. krāsu un/vai skaita precizēšana"
                            ></textarea>
                        </div>
                        <button class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100">
                            <div class="btn__flex">
                                PIRKT
                                <svg class="icon">
                                    <use
                                        xmlns:xlink="http://www.w3.org/1999/xlink"
                                        xlink:href="/img/icons.svg#arrow--right"></use>
                                </svg>
                            </div>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>