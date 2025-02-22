# ==============================
# = Gestion de réservoir d'eau =
# =                            =
# =                    by jano =
# ==============================

var DrainTank = func() {
    var actual_level = getprop("chemin/vers/le niveau/du/reservoir");
    var debit = 30.0; <!--  (à adapter )  -->
    var time = 0.0;

    if ((getprop("/watertank/draining") == 1) {
        setprop("watertank/draining", 0);
        interpolate("chemin/vers/le niveau/du/reservoir",actual_level,0);
    } else {
       setprop("watertank/draining", 0);
       if (actual_level != 0) time = actual_level / debit;
       interpolate("chemin/vers/le niveau/du/reservoir",0 ,time);
    }
}
