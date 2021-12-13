.. _Development:continous-integration:

Continuous Integration (CI)
###########################

[cols="6*.^", frame=none, grid=none]
|===
a|* {blank}
+
--
GHAStatus:doc[]
--

* {blank}
+
--
GHAStatus:base[]
--


a|* {blank}
+
--
GHAStatus:ghdl[]
--
* {blank}
+
--
GHAStatus:gtkwave[]
--
* {blank}
+
--
GHAStatus:iverilog[]
--
* {blank}
+
--
GHAStatus:verilator[]
--
* {blank}
+
--
GHAStatus:xyce[]
--


a|* {blank}
+
--
GHAStatus:apicula[]
--
* {blank}
+
--
GHAStatus:arachne-pnr[]
--
* {blank}
+
--
GHAStatus:ghdl-yosys-plugin[]
--
* {blank}
+
--
GHAStatus:icestorm[]
--
* {blank}
+
--
GHAStatus:nextpnr[]
--
* {blank}
+
--
GHAStatus:openfpgaloader[]
--
* {blank}
+
--
GHAStatus:prjoxide[]
--
* {blank}
+
--
GHAStatus:prjtrellis[]
--
* {blank}
+
--
GHAStatus:symbiflow[]
--
* {blank}
+
--
GHAStatus:yosys[]
--


a|* {blank}
+
--
GHAStatus:boolector[]
--
* {blank}
+
--
GHAStatus:cvc[]
--
* {blank}
+
--
GHAStatus:pono[]
--
* {blank}
+
--
GHAStatus:superprove[]
--
* {blank}
+
--
GHAStatus:symbiyosys[]
--
* {blank}
+
--
GHAStatus:yices2[]
--
* {blank}
+
--
GHAStatus:z3[]
--


a|* {blank}
+
--
GHAStatus:klayout[]
--
* {blank}
+
--
GHAStatus:magic[]
--
* {blank}
+
--
GHAStatus:netgen[]
--
* {blank}
+
--
GHAStatus:vtr[]
--

a|* {blank}
+
--
GHAStatus:formal[]
--
* {blank}
+
--
GHAStatus:sim[]
--
* {blank}
+
--
GHAStatus:impl[]
--
* {blank}
+
--
GHAStatus:prog[]
--

.. note::

   At the moment, there is no triggering mechanism set up between different GitHub repositories.
   All the workflows in this repo are triggered by push events, CRON jobs, or manually.
   