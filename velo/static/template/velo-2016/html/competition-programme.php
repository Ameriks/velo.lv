<?php include_once('head.php'); ?>
<main class="theme--green">
    <?php include_once('competition-primary-heading.php'); ?>
    <?php include_once('secondary-nav.php'); ?>
    <div class="w100 flex--1 flex">
        <div class="inner flex--1 flex direction--column">
            <div class="w100 row border-right no-border--480">                
                <div class="col-xl-17 col-l-15 col-m-24 bgc-dgray border-left no-border--480">
                    <?php include_once('competition-key-info.php'); ?>
                    
                    <div class="w100 bottom-margin--20"></div>
                    <div class="inner no-padding--480">
                        <figure class="img-wrapper w100 bottom-margin--20">
                            <img
                                data-src="/userfiles/poster.jpg"
                                onload="imgLoaded(this)"
                                class="w100"
                            >
                        </figure>
                    </div>
                </div>
                
                <div class="col-xl-7 col-l-9 bgc-dgray border-left no-border--480">
                    <button class="btn btn--60 btn--theme btn--blue-hover btn--blue-active w100">
                        <div class="btn__flex">
                            Pieteikties
                            <svg class="icon btn__icon">
                                <use
                                    xmlns:xlink="http://www.w3.org/1999/xlink"
                                    xlink:href="/img/icons.svg#arrow--right"></use>
                            </svg>
                        </div>
                    </button>
                    <?php include_once('sponsors.php'); ?>
                </div>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>