<?php include_once('head.php'); ?>
<main>
    <div class="w100 flex">
        <div class="inner flex">
            <div class="w100 border-right border-left no-border--480 bottom-padding--80">
                <div class="inner no-padding--480">
                    <div class="row">
                        <div class="col-xl-8 col-l-24"></div>
                        <div class="col-xl-8 col-l-24">
                            <div class="w100 bottom-margin--50"></div>
                            <h1 class="ti fs30 fw700 uppercase w100 bottom-margin--15">REZULTĀTI</h1>
                            <p class="ti fw700 fs14 uppercase bottom-margin--40">Izmanto filtrus lai atlasītu rezultātus</p>

                            <select class="js-form-results-source" style="display:none;"><option class="top" value="" disabled selected>Select Competition</option><option value="3" class="2012">SEB MTB maratons 2012 - 1.posms</option><option value="4" class="2012">SEB MTB maratons 2012 - 2.posms</option><option value="14" class="2012">Rīgas Bērnu mini velomaratons 2012</option><option value="10" class="2012">Tele2 Rīgas velomaratons 2012</option><option value="5" class="2012">SEB MTB maratons 2012 - 3.posms</option><option value="6" class="2012">SEB MTB maratons 2012 - 4.posms</option><option value="7" class="2012">SEB MTB maratons 2012 - 5.posms</option><option value="15" class="2012">21.Latvijas Riteņbraucēju vienības brauciens</option><option value="8" class="2012">SEB MTB maratons 2012 - 6.posms</option><option value="18" class="2013">SEB MTB maratons 2013 - 1.posms</option><option value="24" class="2013">Spices Mini Velomaratons</option><option value="11" class="2013">Tele2 Rīgas velomaratons 2013</option><option value="19" class="2013">SEB MTB maratons 2013 - 2.posms</option><option value="20" class="2013">SEB MTB maratons 2013 - 3.posms</option><option value="21" class="2013">SEB MTB maratons 2013 - 4.posms</option><option value="22" class="2013">SEB MTB maratons 2013 - 5.posms</option><option value="16" class="2013">Latvijas Riteņbraucēju vienības brauciens 2013</option><option value="23" class="2013">SEB MTB maratons 2013 - 6.posms</option><option value="26" class="2014">SEB MTB maratons 2014 - 1.posms</option><option value="27" class="2014">SEB MTB maratons 2014 - 2.posms</option><option value="33" class="2014">Rīgas Bērnu mini velomaratons 2014</option><option value="34" class="2014">Rīgas Velomaratons 2014</option><option value="28" class="2014">SEB MTB maratons 2014 - 3.posms</option><option value="29" class="2014">SEB MTB maratons 2014 - 4.posms</option><option value="30" class="2014">SEB MTB maratons 2014 - 5.posms</option><option value="31" class="2014">SEB MTB maratons 2014 - 6.posms</option><option value="37" class="2014">Baltijas daudzdienu brauciens &quot;Baltijas ceļš&quot; 2014</option><option value="35" class="2014">Latvijas Riteņbraucēju vienības brauciens 2014</option><option value="32" class="2014">SEB MTB maratons 2014 - 7.posms</option><option value="39" class="2015">SEB MTB maratons 2015 - 1.posms</option><option value="40" class="2015">SEB MTB maratons 2015 - 2.posms</option><option value="46" class="2015">Rīgas Bērnu mini velomaratons 2015</option><option value="47" class="2015">Elkor Rīgas Velomaratons 2015</option><option value="41" class="2015">SEB MTB maratons 2015 - 3.posms</option><option value="42" class="2015">SEB MTB maratons 2015 - 4.posms</option><option value="43" class="2015">SEB MTB maratons 2015 - 5.posms</option><option value="44" class="2015">SEB MTB maratons 2015 - 6.posms</option><option value="49" class="2015">Baltijas daudzdienu brauciens UCI</option><option value="48" class="2015">Latvijas Riteņbraucēju vienības brauciens 2015</option><option value="45" class="2015">SEB MTB maratons 2015 - 7.posms</option></select>

                            <form action="" class="w100  js-form-results">
                                <div class="input-wrap w100 bottom-margin--20">

                                    <select class="select js-form-results-input" name="year">
                                        <option value="" disabled selected>Izvēlēties gadu</option>
                                        <option value="2012">2012.gada rezultāti</option>
                                        <option value="2013">2013.gada rezultāti</option>
                                        <option value="2014">2014.gada rezultāti</option>
                                        <option value="2015">2015.gada rezultāti</option>
                                        <option value="2016">2016.gada rezultāti</option>
                                    </select>

                                </div>
                                <div class="input-wrap w100 bottom-margin--20">
                                  <div class="input-wrap w100 bottom-margin--20" style="display:none;">
                                      <select class="select js-form-results-load-area" name="competition">
                                          <option value="" disabled selected>Select Competition</option>
                                      </select>
                                  </div>
                                </div>
                                <button class="btn btn--50 btn--disabled w100  js-form-results-btn" disabled>
                                    <div class="btn__flex">
                                        MEKlēT
                                        <svg class="icon">
                                            <use
                                                xmlns:xlink="http://www.w3.org/1999/xlink"
                                                xlink:href="/img/icons.svg#arrow--right"></use>
                                        </svg>
                                    </div>
                                </button>
                            </form>
                        </div>
                        <div class="col-xl-8 col-l-24"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>
<?php include_once('foot.php'); ?>
