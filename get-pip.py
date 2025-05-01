#!/usr/bin/env python
#
# Hi There!
#
# You may be wondering what this giant blob of binary data here is, you might
# even be worried that we're up to something nefarious (good for you for being
# paranoid!). This is a base85 encoding of a zip file, this zip file contains
# an entire copy of pip (version 25.1).
#
# Pip is a thing that installs packages, pip itself is a package that someone
# might want to install, especially if they're looking to run this get-pip.py
# script. Pip has a lot of code to deal with the security of installing
# packages, various edge cases on various platforms, and other such sort of
# "tribal knowledge" that has been encoded in its code base. Because of this
# we basically include an entire copy of pip inside this blob. We do this
# because the alternatives are attempt to implement a "minipip" that probably
# doesn't do things correctly and has weird edge cases, or compress pip itself
# down into a single file.
#
# If you're wondering how this is created, it is generated using
# `scripts/generate.py` in https://github.com/pypa/get-pip.

import sys

this_python = sys.version_info[:2]
min_version = (3, 9)
if this_python < min_version:
    message_parts = [
        "This script does not work on Python {}.{}.".format(*this_python),
        "The minimum supported Python version is {}.{}.".format(*min_version),
        "Please use https://bootstrap.pypa.io/pip/{}.{}/get-pip.py instead.".format(*this_python),
    ]
    print("ERROR: " + " ".join(message_parts))
    sys.exit(1)


import os.path
import pkgutil
import shutil
import tempfile
import argparse
import importlib
from base64 import b85decode


def include_setuptools(args):
    """
    Install setuptools only if absent, not excluded and when using Python <3.12.
    """
    cli = not args.no_setuptools
    env = not os.environ.get("PIP_NO_SETUPTOOLS")
    absent = not importlib.util.find_spec("setuptools")
    python_lt_3_12 = this_python < (3, 12)
    return cli and env and absent and python_lt_3_12


def include_wheel(args):
    """
    Install wheel only if absent, not excluded and when using Python <3.12.
    """
    cli = not args.no_wheel
    env = not os.environ.get("PIP_NO_WHEEL")
    absent = not importlib.util.find_spec("wheel")
    python_lt_3_12 = this_python < (3, 12)
    return cli and env and absent and python_lt_3_12


def determine_pip_install_arguments():
    pre_parser = argparse.ArgumentParser()
    pre_parser.add_argument("--no-setuptools", action="store_true")
    pre_parser.add_argument("--no-wheel", action="store_true")
    pre, args = pre_parser.parse_known_args()

    args.append("pip")

    if include_setuptools(pre):
        args.append("setuptools")

    if include_wheel(pre):
        args.append("wheel")

    return ["install", "--upgrade", "--force-reinstall"] + args


def monkeypatch_for_cert(tmpdir):
    """Patches `pip install` to provide default certificate with the lowest priority.

    This ensures that the bundled certificates are used unless the user specifies a
    custom cert via any of pip's option passing mechanisms (config, env-var, CLI).

    A monkeypatch is the easiest way to achieve this, without messing too much with
    the rest of pip's internals.
    """
    from pip._internal.commands.install import InstallCommand

    # We want to be using the internal certificates.
    cert_path = os.path.join(tmpdir, "cacert.pem")
    with open(cert_path, "wb") as cert:
        cert.write(pkgutil.get_data("pip._vendor.certifi", "cacert.pem"))

    install_parse_args = InstallCommand.parse_args

    def cert_parse_args(self, args):
        if not self.parser.get_default_values().cert:
            # There are no user provided cert -- force use of bundled cert
            self.parser.defaults["cert"] = cert_path  # calculated above
        return install_parse_args(self, args)

    InstallCommand.parse_args = cert_parse_args


def bootstrap(tmpdir):
    monkeypatch_for_cert(tmpdir)

    # Execute the included pip and use it to install the latest pip and
    # any user-requested packages from PyPI.
    from pip._internal.cli.main import main as pip_entry_point
    args = determine_pip_install_arguments()
    sys.exit(pip_entry_point(args))


def main():
    tmpdir = None
    try:
        # Create a temporary working directory
        tmpdir = tempfile.mkdtemp()

        # Unpack the zipfile into the temporary directory
        pip_zip = os.path.join(tmpdir, "pip.zip")
        with open(pip_zip, "wb") as fp:
            fp.write(b85decode(DATA.replace(b"\n", b"")))

        # Add the zipfile to sys.path so that we can import it
        sys.path.insert(0, pip_zip)

        # Run the bootstrap
        bootstrap(tmpdir=tmpdir)
    finally:
        # Clean up our temporary working directory
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


DATA = b"""
P)h>@6aWAK2ms(onp(ba`VjU2003hF000jF003}la4%n9X>MtBUtcb8c|B0UO2j}6z0X&KUUXrdK~dC
#f)_y$_26w;%50mqfp%s{QkVX{vt7C&5b}6=dAye62s$SU9nhE}D}0jZ7QT~G41O@Cs{W8AFI5FEP~1
J(+rk*rU<;$CaP7I1^1|Pp&Ud1`-)Ht$47h=tSD>J!fm}sV{PrY}+lLd3oUh>R=L2FGW*E^2g*Gxwf^
e82QMwX{#{hK<5(fmSnUab%i{N{v`lg}tduUKS4YCD6gkCjC>0C$JPX}Aa(WN<gmo*)UOepU0{`twS&
X(DpBFPL}t?ulkS<+%qo>R=ItXWk@_9-EstuX4u;Q}tnY|KAUO9KQH000080N_cQT5tES*SrA$09FG4
01p5F0B~t=FJE76VQFq(UoLQYT~bSL+b|5i`&SU@!Oq~iIS)&L9d|8u8wNv=>6nNu38Ea&`}HFgyJ@G
B9{e8sD4K$g2|O2c-|@;t@dR%;`5Qu6f^i+#IYx8|79X$VF3?d#n|xfMkA8wQAoLVDffU76;J#O)CYU
tTKs|(rtOUt}xq0efX64y=-}wYe4gv+Rewsv@!47DzwFn{pMIm#X%sAFClIW>99{f@Za2e3a^UYte1H
%y3G<XNkQ|9}&5xy4m@b>HUTlK2Lp_T}m3nsgC)$#bX09kug6MU#nM~&r24-0~c2yu2!TgU+z6-O~;x
-O@YkJ|0dA=sY-F^F})aITrzTyS?O7N5T~%P_vE*{#XPt(tDzVC+>eZ42i!91eGvPx8>ysJFuZiRYzl
Cqu4no3L)R_c2M{&P)haML0zYtRpKw0?HZ~t=E9}0<93*a^reKp2wsiXosq<ZDnF1d&EGAaqKtH_neS
PAHxCm8ml!jzxyu~m0X`+&pMkth|PEP|9MZ~c>Fv#$q{3!PIV@d3Fa6TvSqmUyJeY&DcVg-E}?LbjUB
1cn%!C6%kRp-;$05^P^$8se4pYUP)h>@6aWAK2ms(onp!0s+MCq^00625000#L003}la4%n9aA|NYa&
>NQWpZC%E^v8$RKZT$KoGtAD+Y6@Eg2U<FO8b25(+98k|yC$QMB6FW3trVHM?sX3-RxrvEu|HS|5`2?
#!DvZ{9i#!^sA-#v|ZHX1;8}ua$$$)Ge3-YE>ujN70@J3Ari?w5UCxep1%xiq>fmEIFl6B?A3xSz!*+
f%5d4fHxHF8jFN1eGgxmyrJk!>JJ`PlvdTodP;jzGLU-v4$e!DeT^^-gWwoG9{qx@+7nu*j3%O0ExlT
)Qu!9LHD<rTVdnX)YFvjtYyFyD&vwBjri>H>L!H(!_=TwzaVV^*pl)kx9tbG)rYeKk&*k^&wU|$S++5
8k3m8Lmp1|ig2!b4ofsJt9M%#5f0yqZW);I!nuZ_h3=&|S<t07Fo^uZ_{br~@f#=;Yj$U`;(tAdH81G
dtIxgDL|!527SGwPA0atMpokz|vN@=>?TPxwZ$eyWfgq*)nizNtGA>RzSi7l<rAHp<fZ*YWd9OjL<pC
0`-(^SbBvc*e<_kOR)~4y#|qJb+79eoYPoqsexiL7;KF37$iNlJrBe)v94HAxWgY-1M`ySV^S`=)H;W
rfnNd=BD9j^C(9!`E+^~bTjYIOSMWXnUUkswu2LA(yuR-&e6V?Xk1EF)<bZvEMJ0y$Y6Fg6N~B1{9>{
Y^XYU+CfY_u!@m%Gi-d@I{#hxVgPE$YI@mc<6gykr_e}b+f9t|3q=xfugZ)@gfN(Wtk;Ae`plHgH3na
ii$Ja*F(o1`fzI*wHS@|Is4%u)thLF4yj@}qyYiY&_b_ZOX8r<ua?m6w*+#YIjH_+PqgStb$qm-FIbe
OR3ZJ)6v#2F+bdz0jmf?H3OX0+%u`H!#>%fBrv1Y-*UW9nT9_LmT00^x<!e0#`D6hoq%(25)*L`vqOu
b-sZ>l2ROe(l1bGhRx+qTh)+F%!n<s*GP3kfkRyB0pZ*hMM~eP)h>@6aWAK2ms(onp(}rz%{@C0015V
000aC003}la4&FqE_8WtWn?9eu};M>3`O^T#obt*`VR~YY;QnfHmzwbC3ciJh5S8E87&>(bBYv517Wk
ANp~bsMyYmG$}2ukNeuDHNG^#ptMd*~JcpmA56q`#0W5TpB>IYnZ>tlx>JJR-$h|q#9KFT3l$ThGovM
`Z`h1@k{0zqrjTIlGh#re*%w%#go%(3HWDhs}=jz2OtQ*5LjXNW#DIpx4DusYoy!{s5eCbN6)&t+Mou
mghxP_Ew!2Ru`@Lf_lF*R=M@&`~$0|XQR000O8;7OWVQz>BIHvs?u0RjL382|tPaA|NaUukZ1WpZv|Y
%gD5X>MtBUtcb8d38~-PQyS9-R~=`vb0jUEJ#2l7?~<q*s2O$6DP5BxjWeoRsJ3)r62}wxu>V6=jZ2^
^8h*(N*&NpGAry!bPI1qDW?#fYiCKJ;y)-UvT=S?igML|#N0V|1C&T-+?m&U1H&i^Cxkl0h>f8(GeSt
y!hmM@*7^>0ZxDICF`IKwbq{?g1(QI~>zLfakj-+)%@|R<n`imIL!EOCnl4aU2kvC|v&LcG>LAL;BRs
)tPPl>FXUnWR2liI0)q792lR#k<<WI|Ni6O@Z>YOA;1gV*d3TSV!hA@Fx4{=_Su|>vITZ+Yw)Vl?|m_
=wBx}<;xHCT095Jc!zi|neZBkjkNuk%oqsf5b9u1I7=sqXI{AN)1o^8a@Yk4bqd+1TI9oO!O1FHsnE<
n%)>1#R3HP)h>@6aWAK2ms(onp)5PLj4d80068i000^Q003}la4%nJZggdGZeeUMVs&Y3WM5@&b}n#v
)f!!M+qm&vzXHcRgltLP$5TfWwY?<Hou_HyNt|nMJQ^NFLKbU^<N>5*oyY&Zy9<B>K}yMW`f_@(OmKI
x-@91I^SqZ`QReKTx-Uds?RnL*PV$^>YrzUxmuXwn70WwORJTm#g>2adG2qejyv3r}H??S4S>N8ml6k
D9`L9XaU0H0*qbyq9|9|YETK>=;MA|I2qTaKtE=!)_#*%4(_af(l=dX*bRWR+b;r-idk!F08W_Q=H+P
_DR4ZzP=7s;z1FJArQ^4$+1yKK2gHzg0*TM#H@?;G4KEkpK^!{c?=;5#H1vQHJfS}3AT(ZtC;uku>N4
Q!X9%<(-J5|yO)`bj+wDCR|yY>Sd72}>m|CuN<Hb}iaP1)KpRaaI<w1PLl2X7KBVSBYMn!!h)Fgj?Pw
4OkHLAF78=@cuz&JHF?0g!a5m^R!KEIyv8_UD+mla1=$xT9~8NwM8jo?H;{~E<U_`|MB89e6L)a1;Ky
q3c=6sB)d%`>Ws@?3t3v0$*_DHwdMOJ$qUgt4LrYw4YRfu$B^M`c$?f6RW8Btw_~qbE*N}fhyyr(&=P
TQ0eI}UxKgWcXmPPXHNnf338xsueoJe9l2qv)oF`Z;7GMho2Fbg|PnS%#B4iu-4p{V8<*+y8!#A+D*8
Y4$aJaBmtP0+CqGEmu*Z~7^Quft~Z5S^l$5q@ZD^pNpawYh-cu;7xIY?KuN#aXhZbORkVgGk^#T6)i5
F$nZkP5%XFC_5Lz?(NIY&yIm&xGZ{O?}UUeTa<}k_pCiHbq62TWQ=_W};|XIfeq)M<@wkT74S2j|=mx
g2w2YoUf}YOc@Cn*C#naUL_{v!5?@F>cjA6Z4GjQ(%?H~SI2e-nSnp>tZP-qfpwt8+8t+ECj>Zid5n-
cdOLc~f{0%43h-d5lCj1~DVq$g9I7l`$rfB3(X9vp<O<Mm8_L&2)QZ*Euuk8y?nK75i9quB3ch_iNd>
XsP!8_7AAmWLZN(?}O;xv=KwL;vupbQef2Jfk)E!irUD`knLmXM}Irxc^P)n|Y2gE6I4zm7+E1=PsU8
1_u)}ooE5>$Br6{Z!ch~BfDg0(!xJ*4(=FqN-33>LQU*D~J9oM&~;^?UX;^AfZ%nS_fZiJPO>2OT-&Q
9>$6u#)MZmdYWZc2K~Lyh1@!-D3t^@$gA@V78-@8sB5I+f+jW+jK440w9(*2EO!*mB{_zYb(e5!7r%V
u1fFIqC{^a0zMFqL9L)tuzm}hf*Y_*@U#Wj+8nLb7vFuO74(4=B*C^~pO(dM012_m>MiOL>?Ozk1KaL
WnYO5BkRW89Ba3Ibgrz_X#W~S^72lYOY*(`Qf5E={hSgAd4}$0rmFCC}1w>p&1;Zw25wVqN>C)C@Y=O
5r5bvt`P+=tQ3ykg^Dj_86$Q?R&^}IzTQ(S|0+B+V0(7U)CfzN=-*oH$uK*)k9IrDqxA0!P<>Fs9Z2q
7DJ!rFH8$68Vfj?tRPoKGo~vInJR;M*qt)MtKb4z1p>ckNf?K9Z$X&h}}A0>S^fV+2X8OoKYpIZCA>C
?Soc=5e;3%oLHnGOxx(*~ePE8WraF<)_QHuak>+KY>QddV?XBC=T=0wdhO+=!-(4stT#p>N5Qvied<h
Z)ggkZ}j<}x~P1^94&<mA%h?op`)U49Tn|+DyE>GdFa1oiuuJrPPo&RO)jZbrTl`nUpru?w4DSaTNC%
lgy7h;^4u>0+8^s7zE8^z{WGv)cFIspxjgq3nyJ9S42Iz?h9=*_Fw2(6&)BO@w)GzJjmns9ZHIpZZY9
CtS=@lrVr>AYgGVT_HJEJ#*`SEvd}&6#Ao$>HCO#2crxU$vAAGA_^PE?B2xr+@mraAhAHWXMACq*{53
u_?tga4J4}__Y4hg=CH?TFv)qG_}=~U}r@c_=rD=3SQ<W^qSZlk|=gNx$%W!sFI+cq&J;_=q_F-N-?I
xaBC6aYV_j@Y06C>b(UQ}DbvfqKT?fDgf0Bo}p~%@`>&LT02~gwo4+f?10KdhE1BJ14qBg?~v|H_P<|
o(cc~Qq|(EA538EjQVK%)K}tZIV(BUtu)W^8;z^n#oB9S{XgAM?_qN_yUlzBm<4sJg3<?6B7dT=U`9(
*nsa)-ncbOQ+S^Z1XVD;*P82u{v7xq+k|q?UA{e1Dq$do_IN(QUAgerNU_}N=O}C+d%4fXpnaW|<^7d
Jbl9=x4c|OG%d6h|<Cp`-4Hix)D*<CY!u?J4AI2WNoyv0%m1;q07mHiMh!|rNa3&tA+b}PW~;C#9l&>
1Yf=Qw%*8$FIlVVPZ`Kj;nwJ4;=?k<PigeD(eHk64wje!l+k{kwPXKYhIT@bU8cVpt=HfyC3`4JLn#N
~E1d>M~D8Kt_TaweJ9l?yP~w2G*5=YN&yTWm6WdX-Fh*0;@tbbow+QH%|TQ0nAcX*W{_2#2=@=KpZdG
u&XLA<T>FCxU0}5^S<>?0-mDYOXKYE<aSTmj~=L{968Q_$RDx<XNb#w_;-WzzMGejJuV(HPK)dH7y&v
X3w{jhklxsY?eU}robhb*#`{z#XGH^3BS!H%@|YM*xR<`u9%#4GIMSg#W9z1F{C>M>Y>dxdQ~Vo^i+y
Il@u2@~$Fn<oWG5X<;IIPPRWpjEmUYmK8d>3q+8thn{W*I*um{;momkm-SOewoCSs7Bw<UD+?to-zPP
D#0op8wEhZM3;9uRY^#jT}93Xgs#$smf&Q2)Qda+?O5G51}e=#34a^4+w+J7ZY?T&mT?`_np^!s~&(D
KyOkPmF+lH;>y-=+7WT0=80T4p$!hz^WefSxWUa+LW1R>|gvjR7?H<c`qy4^2j)PUP@Y|4j7K1(0jM=
;-M9Al19J87P89hQP`NMC6YQ)Q1uk`J)FjKpm=0^p6$}Akb62xaJ-*jvf){=Ei$#!OtDv1jQ6Ry!<nx
nvKVS~ZpMe<b*$y!{-a0qFiUz*!F-Vi-vNm`K6yzuG%FM+CYu#Fui12%iBPLC9Z%;NMQ#v!en0KQ*e9
Ge&RND_i$YSQfgya{$y}U-=E~%RtbKSU#+z1b>pdE2o>r?zo7~g1QJK$WUq<`0#I^1aMLPr-6V;FcaY
s-%mBOin<9tXBBTib^WCqf>KVdU8krm9v$eYW5|MOzWUez>C61pR0pFX_(n>!k{whE1vhb*r5J(tIa@
<o>z;IyMl4XezLv*sxA4?t=-kfbtEgGP0~(ZBxF@Gp*gthX}-RnI$C&Y<VU-DBvz?A}>TDd>j6q1azr
pb6b0{Yc7@ZIs5HM)tgh@iV=B7`H!4@1e8RKyCa+NibfcDH{G6mUSofcVMn9vOR~^D<68R^GxHlfnnG
&-~ZD`mS!CHKYB+hZryR&czAWhiB*4bGuEOd;`oiHb>p<RUKAC#IHijEP@Y0mb=1j`I`j)Aus3H(HD8
*cbb$6OQrBRSxx|@LhV+CoM0n$&vs6T_n*;iceJ_X0q|ta6${KI*+DzaDdeJ_Y&_%%!aNCtoD;+Apbd
=Tm22Z^>gFMn8J!G6xC*6mns!Y;beSzi>+1Ggo_=f@~%ABsqzScx@>@@bZY}F7xo>7d3oCtWm<0fO6J
f5@mP{R?n!a?JvzQ^mkT_+vH7CZ@BK>gE&YFpf@Q$4gl*s(#Mtgi@=S>*+}%a@|z+Q)hxoe$MLF&6lX
?G}G2anIj^zDhq}FNVwG*B388{V+~J=<{Z9>qYnXR=dZ`&l1+x_Gd|26tVwP1A+w0p{PqU|Hcz?DvmS
)ugar&bgH4km8w0YZdIj^cuX{OHVLNe=|l6RQl1z_Mv=$<>`;vbZ%R1E`Cfu-N8ZdqmyknGPg-jMCkf
vO0lIkfmKA0oXzFH=XD1@~q2CWAohVTgS_8wH?H0r8jES@kZoH@f0S3^UZ`SK+-%cH9LQrTl3;f&Vdf
K!&J4A#Y5mp3PI8Gi2u5G7t8?&)HVZ0KK<5m!ocgUA<2>42H?Y!U-!bJq<g+ya*>v?O)LF4~$JWq*0f
QXH;9`m@vEHv=giVl)up5XFl*wmmAg2Ep7wGL+ZRCD_zgO=qyL4+8Xwb16tmIdVXFCj~SF7*L>mOAA4
`jBAvU^T;MeE{IRIZBwUxzNeua})qFGHGUU0?d7*MYVg9ncEiglPrJhT@F9Rc*F+e$)n2>4KQZW`B~C
56(I}LGy&CX4~IuMjLU4b^~OI4v9DS+15*l`o0a|!-Mpi(e&5ya8~6IxcNc>GLil?q+ELxmHB3aOeM*
<qAz(DPn7`}(7k^OmJ4VD4@ITrla4bLuF;d}=mA*vUKlX`Dq=n?L)?V(LlJ@2Kg%GvygT;RVP)h>@6a
WAK2ms(onp#nL_E!oF004j}000&M003}la4%nJZggdGZeeUMV_{=xWiD`e-CAvr+r|<8e!pU?zz9{yy
wq^qR)C7S&Lwu?mmqfF4~GM>5?9jN6v=RxCo4t&d!LzIl1q`iT$-j0Dj2f3FSGML&n#~?n>~}8y%Miv
E_dpnayy&NE-v(;EGjGZ((E(6ZXQ3FB5!_Y#crqbUGrF&i)~dLL@6!p5PtYuJh};cDzUs7f0~~b;w!z
e3-MALe7`BJE^?V&crv<-lUtRiMHQEF^HI`Sv6Va1P<SVI3!!tXs<Kk}PI7rr{gGQ$84$gTVr_NSlHA
C=$n{2M`bWj&LS~pS7>w1YjbdioeJ}D`>`CA6mCC->nc}S@I}b&wG83n|QX8ApRn`#ribuY$vO9KVI{
(<Le~I6BEIkq<&06MaY%z--TXiTCaMY?5&yJm<f{ADvv&l!Dr)HW8WNEcQ9+23A<h!^aFHx0PHSQAcl
zqu#QNk)tlKI8Oo9|wH^Wt^#_qT6eC$FEry2AQdQE6<5$>rdW7pdBcgxnF#Zfuk;*?X>ytrh}bH*@ju
FZ5%1A@G3@f2V9+<w9amt}`XfUOsyCSQJ|f5ef3P>J*c=(+-0(>8v=d52cAxP=zqbM|Co*cU29~GOCo
7gj&ohnk{AvF<Z{&3!!pTS1OTaqcyLbGrh_k?*k}yr$;7M`36RcX1snjpT~RkDb+h=Yy?GIY%*z#;E-
%3c?v1k5KV62qCEdllvQ!7Q)S?@6uqgpn8wJqs6;BQ6l^VW8*{;=mc;+T?I4pc#XD@Rio%jsEPnG;+?
?xnvEpHGZIdK2D%&nX3Sf&h|GLOM!>r7@gn{RAyKml3fqexh$qU<&5#YEmF*#1G4P=elscs`39d}z+{
q1yqz%RTkar5kr5ZoHiJSk+!5yXsB_8~92>9~jJ-zf59Y$DCj52#04aj1<IYt=IQq0qTX#ZlXR$4;v`
`g|tdD{+)L2oz$cas>}kLgs>^A49dl6HcisZ%H`ZLL6byBLCbrI|Fhbh=oegKC;;N-@ODw8%fU^4C>v
Uvi2=_#5AHB0gTAZdGWTAJIe3@Ihm*3X&YIAn{`o>xP|eaKp$}BlnA~5V+P)5OI9QWenR47PtuV8XS+
>r-71b-iguw5o1V<YXSdVgOlOMT+1GtqH<VSHk-?FsUN=E;YB`%CJPTLPTEe3=LfgK`H(8yku;>U^h7
R%rypkk5=p4U%DI!a>b`A)^6E;PuoG0lld$?9)#8j9R{%M@|t!tg7oV~VNRe=@3i9R5csuBf`%532*U
Y=l@ygeO52p5CYRL13rRK8ZUx~g;RSe*HVa|)NRm|Ao2MzI{l0YRYGI@9(fs5Hj`fxWe*Szcc5AW^-J
vG}q)mGTnR<5C+_D|7kBM}K}Y^swvMc~NJBoDT*mWn!xrda&D%Q@ZWgy>e1g9D*E2C)>j1ZHmaxvrM?
CW3{y*2k#R`A9N<GfSysCx+1+GQ6m>xO3W}ak^Az=0;aT%KFZS`bq0Q83oA1)U`xzJ(0}M2``U<1A@e
g`HIK#f;;3$EThA`W8|@%JBEC>`DYb_V(piwo1c^&xY$U#rE`o@spo0Ic!lK(MdOnfha+ER8QCE*lfw
;#c)PGA(3&$p(lNign@Dyc0EyJR$xBp0tQIc}WjeWJ|l7;x}tpq(fETH!F+fJe;e_cD#u9uH)7GBKjN
6W|E!{g<X?%~Pu=BAU@S9K;eC^v{a)Lk_!G>Z;dCJuT!c-fUtu0p`XK^4N51PRfVF|bX^@vH{Ig07B^
5pQORjW9d*==Kw$m+m?cn93Xu=YvT~E~jvvgvdtpH4lk*RUG_9^m9IbMAWKl!Dr0bAKO97F9l&<V_QN
u=T>O=BohpI8?E*&K%`Fy65Bk_QHmcP45eKKB?h@HG?0;5ks6`%y09+}WybB3O0TM_sG9WRnTvWjrpv
T}lLR^sU8HG@7^HNI0I>*dt2Cj^yL29ep2#opUIpSqaSde#>Lwtn48<f1BBQBKRC5*%K^#fG%J0KKz$
K8JFW})B_fw4rx^Fejaf`y3H{$Pk2Yr3DM6h$MbLe(kgB|h_K>G~c$A1>92H5kz;9h}P9I5U0zxfhlI
sFkbdlfF0`AHCnVt~Mi(YFNQX)Q6r7pzE7gPHRM7kE5S8Ak(?d4SvTd8E0lC_YlIuFD`T5t+TVsP^q3
N<fikC$flQtc*<*GdQ+wE6BO<aB}Fh%pjbmzN~4|8(MjNSYwF#FUL~{PmA12z$wZP9a%1;{zSjN>b#U
PV4dq9Y88vCco&QK(uY@wmDA!!v~lERjZe{$u14w(E|bn05Y|8{?D-=8B93F4goxmlmRMfwZ7iMP7)5
kt9Y_s|Mg1iWlRSp9w(H%gQhJ3!4|RolO*mt%FsxF<Y8q(Y_jS$}siouK_AMRz2McoC>&@Q5mm?r%qd
s=2@d$1zCTIWgo~mB~d~???Q$aa?%bxGOm<;C|6YfEW8+@J*yRE2C8%?;QhIah-AvF2zq}>h|5cUX4E
6hvY**kWuR`%1vM6q8DFR!9-L1!c93ecIqFmu281}N`Yx`i{@9T4WMyxZ#3AE1wO>6N>Qin_Dsy_N1-
ZS*c}NRm>4&TG}1aNy=l34C14$BEyqrhwSs0C#T{r)pjAqQNYEW-oSV>?n4_OfDX{^o;)yuPCOo@y%(
WT)%semZMTZ0VQ%T2vNjV8Z83l7q;#L)VRecp}>-(^I6Zu!%ryxaK-%IDkmYFlH1sb`cX0;s`oSTH%^
jV$%2N~^{bb%+Uzft-Q16f&Q)VsQUg3R*tiLMY@__A>Qi!{9Mfn2-_v{>S3jlP`5+~90^K7aB#Vh~Ue
VP<hqFz0s;5JFDhh6Eqh6xz_z&pM=N)#tDuE>e=ys0fLKJsC=PLE4Qk)mH{T#*jnDcFOQAxm${<Y?58
sUv0I!<Ek#rCRyr`>l2y4POyF1h2YZ=YYiO5Q)ex_X&Bd;0A8Ro{TStXKmfoRR~-F-hI+aJwY1<^Wmt
8Dm|a-T7YSZ3gX0`g6({0TW~Cwo9ywBJ+jmOg#({R{iFXC%WyJ?jHJ!+}(UoB-<AlblJjpvCVq7H0j=
XB)+AjH$zd&OT0y{=czgL!nxp5oWB<6b(*7eW7oSx_bE$(Bw(kNAf{{cgkA-VCyj}N;mSxC>XVK5!VG
m`HLLCR;h$#1R61JtuA0|MR5+$9(ot49i2qbg(yom9I8x+Ro^wH(4$4&Yz|1F#%ebi1g@%ndoe@XNOy
mC3J>dIFmV<1=@OqF{xZ{w55H)1vF&B>S2=)4nSymjK^t(!K)V4-2BiitQGztAL0!XgtRA1Ryl}wF$B
XrKdx>CD*++1I8i<<fX2Wt)U7jB30D`S6+H!M?cOcIy8n_Hwo!#%l=MQ`_=C;MO68~X}0;BfMesdt)V
?H8RHNO!L@e-n)aS;~cSa3dECd!*h&c4r6mZtFsd@ZaI9mk@BAjRkw-4v;h!3Yq#}Xs+GbRn?n`o3L(
0b0h!LcVozmEiuws%x!m=Yk?%tWiYsLeK^xNO4H8}BLx<DiJenbG7DeGdd5RLAjP-c`B@P4>jO!&8ny
zVx>wWvKwsgj{$q%I0@w1~`K*}r969i!PWh4Bu?SS+-=<GVd=|q07ZQIhGjk>~ZR*}`|J7I&sm(#5Pf
FX6Lwzo)G)aM>vjRB874E2CMHZr+*ZH<sc93VJzWCA~VzsVP+z*=lTs(Fs6botI0kwWTWc945vy@Fs$
Dd=V_O-5ye!^7oRO|nqF5jf3Hh^E66}PH7R+?UV*r_%@5dUXjtKI@Q)>t3@?#)+kmi!X1Q@i@1*6>XK
hB+VEb=TY75`gOR4_|!w<S_*U^4N}UE6-`PenNjjKsPfz=cK_QxAeJ>vFI~<<19pfATc!11G?bt-M}=
*^M-NDG1&(uc4!j+GW}5jJ4*VKD6y`0f^Re2IS9zAc3#J?yQkcNiLy(Ce$d=%E0L?CfGt2^!ZqmAX>x
i^cV{}eWMG2vrSq{Y5i{#9Ec<k9;X;`IR_eSp`WH}30|XQR000O8;7OWVaQ7Ls)DQpwwKf0%9smFUaA
|NaUukZ1WpZv|Y%gPPZf0p`b#h^JX>V>WaCyyJZExGi5&o`UvB%&L2`4j6TNFJ3YU?{YIpZ8Vu#?;sh
QOo6mBof42`*(vHQe9cXJ&WFU6QhWK|j<8Vu{?Ho%gpL2SM;-k+0I5Z57vPk&8{7$2W2#^I9lbZ_Cl>
ve-yb%W9M6MONJGW}^d<#~V2k;!ugZDy?goi!>KY1|(K#CRK<<w{f<mRiEg$h?OdqX<W-h+@<we#2Uz
f_$+r=bcQd0u(?iiyCSV$Dj>0ByvF83NV_Hsy-MS}CM<+X^P5bHyP`@&BGs}=0p>>Btz`w&*V3S7X~c
;KjGQRrv=U1?dQ}yhQ4j>9QMxIMsy187xKgsR&$40}XVQKvl>MZ3YD54;y({Tp^Y}2|O~p~Vtf%4x42
-WcITfd=!uK<I_hDD!>v>5i#o1JR*p`5;;go3^Mrn>scooVoOUcWWg**n?LU@upuBxJ%_Mg9jIDRa)S
#nm?KgiP}PGmA2O@_|d)@jxp5tn6>R%-9M5W*_s+Aja)<m~ADm&^Ujp*lAXZ*F9LiYMUh-W{7%E$wod
t8FDCU^K<&?PfH(i0?F=?^#4*?nx}{z7{XU<r<LIah{BRPV)pCj1a~FeGjHW)zxG)`tkhi&B@#7hr`R
`v%`1CSQij>X`TimU0Fhf%#_q`=-gm*eD*1#^_S7f+q3hF<0IO5D=P&V0CupJSqbfWAwEDKKjT0pij}
XJigXnk8&@(M=_PZfR*U=N<?+Ql*n%3s13e#!uFFy`(^b0U6>m?^e>gmy2RB)99cOyg<xbUdBYsH}$!
ji8J{->jmDW<fzxtF`^)}8H;yAxet0HIH_rQX*c_8y!y@BQR{^WgR81?4l^w=(oJ{?~0QrK7JEO$YFB
Ey9#C@A6ir{jx@lcVG4{Nm{N0@O0qp{8SMz7gH_GhuH(<2>gh9X<MVczSXaot_^aMdxRy|7-xdAbj8i
a5TzT6|uZg%W)Kur->qH1cY{W{^58g-o?9XDIfuMDh1o*7ZKMr9L~1J(?aA$wTZLz-;%rxL4Yev<Vr-
%3x+$U|7NUl;^1%ed&WG32YMHOmc~1hdMNk{Vp}C|;wk~#SZ`FZt(H=ZrNh{wV&6L<FGjE!!kmA>`tC
r}B&=ka#Y?DsL^^p8On4>Knpdehu4+ZjcN`qxrN*fP>*|lQ1qrsuvz;g_xdP*|0+tPaDBe&Za8$YW?;
}lpk}3oMxq;jxFs4I3`NS)HS<EatK^TCQHH8&k+8`py%|&3VLYM+Z<K_*s?`OFaNg)+)2KVY15R!s|8
5{#g9~)8N2uMbu2s{w0;JvKYajC?v*or%Z80>*yN$M}PVTJdE)5A+(2ie5Q-&+Wi=2I1?*wJ^<V~>JK
mtmnQv$P(A{;7C9G3<j@MxLjLILMBfc@$u-$b(H=J{m@9bj?=12Q0g4a4b{^7rqYvRiyctK21f(`%T0
OYDKR|6ecEw<UK4@dN3wGXmn{Y;$Q9(IvD4Ary*p9q&(@D{+SFQgT60!kAdisA-|LmDmln;@Sk8ZZ5A
+kedit0<91aC4gEqRlgqouFtL20qaD5&w(KF$2>re}-*r#3A=ynkOUZZ5#8sEoi|#t|epuJ%=(J0i+4
=yzTV^m=Uw<1H^%K}ky5uB_-B=cCHF#eYw}?Cn)+RW-ui$;ioZ{sY7C;FB*&zd>FMgtCQb~sNVVx?Wk
-{Pb)>^^)w9pUVpTH|4A*ta%l?ZIUNXZ@<Rse6a%XAFHGsWksx~L?FU7fA=veXob5P-Enws``7hYecG
jW4mM1un922Cu8wfMQ@SJr;0o3X`IvuM3<+A6(aDkFZBmRzU6+Ds~I($QpAYW3?l0YC+IZ8)1MBaFXE
}*dmGRSkn(+gsejFN|(qyjF2@Y?7fkhrF9e`2hUbhtS&O*&<uzdNL(}Ilo3UPS(DAOKUz?VRpgSr6n$
vDxZ0K+jvC05QS%OF+CU`C$dl7<#=L!FqC+R*&pcng*9Uv6nBKPx4oZ+FMioeI?QsV}ttpEZNB{^K==
=Rc5E94Zx(|<GBEo9_u!+ktA}?~+4!V;`Z>RsH{YJbGE$hKq`_W&}B0O)AZ+ZJd{2-Sxg|a(JP-H3UD
qemjYIL!L$2Z_aqaa)sc_&0V!B(?g;Nb#>!p~H6vhT%$bm88k%+zo2OABVT`A#zRv%+TALkAJ9;T|6R
kugB+_1K~J4_|rcrbv(%%cNz)leAOFU9{FjVqr@funU+SRcNYfy_7=_7&M!NlLFezuSJ)2z>Oi}iEC&
%XGV@<`S#<$a88N9HDxW<rY8hEs*6Y_$X*)i8h_9xcZSRhj(*zpa!6%&yH0P`Qq}NtX;G#1u5BwAx?K
t>p{(kz-a8%x_ID<A_6Dm}x}?GPSf8jL6T*l*L2D#+wd=SM9jP@ph*&LqBA3-+H=bPmVbP|jT&{}~M2
au$ZU&(df-MUX!Z)hrn{5}kdc_(&$V0!Mp+uIVf=FNrp$0n<<a`i0a-x)3o^c<b0p{`8Jz~_sTJwNll
U%EvJ;7H7M#e-7AlD}PpuwZytwema{+1gk-N+TXNI)lUsC=Nhj=M(sM?dLSSa>>lrc7IUuCS{oNfZ?W
a(p4$qK4TD<WM-mD8&X*l?sN{Hq!-*umubCACMbw%52vG7Mv9bi_0}p6Es0Q=2|n>9+~J&RsOQJuQ}c
?iw(km66$i)gW4;*Jf1Kc_C?5*iw~mTz2*Hw;0Rmo5%yHebVdRnc60C8a2nwcB`u!lpCMx{OVcS@$G0
+Syn>rw47!cx?TX+|MQNK#j~Ts}vzQ%@`|0{p*0HHArH5tHQ3}H)VvT`s)3;%ZHMkH4rVqA`Rb-B~E!
2sR82y;Vagy{Fj|SF3>|>7}BX0+PH$-3gyk4-8fd#ff?C#ja)#nH}+c-P+1mdXPHs7aw!wUD2)<0k0z
TVaRPt*`Xq@zrd`xrBynejet&;JM7KcL3_)cO&{X6rETE4eAad+il{ZSADkeRI%FTD?`=#hNG$FbR9B
pI>FrPw)nLb%yLf_qt7dxJr}x>qRKuqf7)a#B1)sQ!u&S-h@F9RL@m>aO%fRyyMhnQzC_mSGBHKU4jO
Q@jZu4NuKZ-hR=_>jo)F~^pnW!Y5(B_A=ua>3H2pjYh&M5mE>gqU<0J99h?Pn-msrFKWV&FJNUNJSZS
|7@Hn9x&0(6aigEBumFk475Z@|Piz}_19l;(mGDtQmu$HivUr=!<Uv%yL$k=wK@R^;HhWaGfmr9g$$*
1VTVw|^mGu`k>N=AK|_A)B^;UvB&Wo~5~+yxU-<5hpHqeFbec;z2plCSeiHYNfh`$-u6{670z1&6sYx
?;&Hk)ZbF3Zxasa05m3%}_(UXKEi%Rx;p+z2^Et|1aKG=`B=GRK*rYn$FA%r{glLfqRrZT@4gLeILA+
Ph2H&U1VycrCT6re-FllK`S7m$BBe@f+D9`#;Q_OpZVgI)Zkmyl-Gn4-LH8_8kYQ{te`Mey=#eY)A5#
Kzq0oX{7|$T_EkEMM0$I<b7X;}R9M3_*cTS%R(D*CbJXBMaal|WCKZoV;3@~4{;?2p&0FfOv?hz{19=
FwCmwvKvbQ18t6pyDp0rGW+t~A!2ExKIcvI`>O^%ZFn*;xwwuH;w&fNn^O5+QQuR5IxuQlPmx@vCu7F
U0my+-ah7gz9eiM-9XS+*GTv069#oxaP@Y00<rME;(hvq-kA{(VCZoJI&-X6GIhMnDi-)O-Mwt`H%XL
HSP&8cq8{^TAfzKD|vaqUF49D5E)9>Dy(RsjyaVwT&`k?ES5=&EIraS9m#T3yUk#2G!g&3=4v<`uWkI
d-A%v7LRY{ot48;!*@Q7JlSWx{8qgb<EGE|t(w@tI<?32d#?0DmxXD*m80I<PBzTQ(OKhGSObAubLwX
)OWhnWZPvDwQ`8|ydV9PkYh%q}Tq3F_<4(>r=~^@6rOTm)2f8)7@~>PwUCLS4v){_<x=?Z)ym7n|F?R
~@4sVa}-xv@*4yK~Zjy?RNJMFsKE^SRQ?sAXx*=DlP%BJSzCq3<FlK}9+taTs@?YK$bhc<OxLPd#c%L
WEJ>HAbOAJj^rN1YbNbGhH}>ak%Kr-$3xwKghU;_17+q@Y&OHJc^y)v`+QWLt|RzSpw3WYVCT7Q^l?-
c8B>t&6O^Eef5bM}>~BI5btZ)pfU)d7Cci3%2;ynx>kzcMOc01J0(K4fl|X7~0*K&|dUX25c0k>-=d%
3;ENsV0!1~Nr)m=4=W(yvv0?55V@a|*EY3I+*B<V#=LXlU=sT=Pw`eBN&0`Fm#DdLDWzD~b*W~rUfm#
t+FsL;)vIz>#;?k>e1+V6E7hw%fB%<1Jtqksn*18hi9wet^7$$-6BDYr3cK%6_aK(*7`_a_TRB(f?ho
^4uDLXj2M=(^)Agsa{pYjkuit+?oA~fK|37)s=7%pxz9N@$r+IGem{h+!H7?8>eQF%pfXnN8wP1#WW;
P+G?v6Rw-0ZXzyYZz9#Y1XpJ+^88vcH_|zsKOsPbKze_C#g8e8)pLX+KvSErxu<AGY3_@8eCeMGmW-4
CN6mq-{%@a&6`UD0$yN5%jIR9(J`lFffL7FqlI^jU9o8E@jPU2W2h>>~o5NO=Fd!pk}BiT-}Sbk@7p9
nfh*U(9E~G_DrV{+g0**k$<)0Y09JbRn8oeq1xV8#ekG!Lk%MJEHDxZhgG1M!0UH<NQe_{mvO`(VBhc
up}{~HPLg#))thi*kOPe^)1t)kt3S^cc64qit>u-bN86kK9L`;LsYFO^L~Ggt;@4k)ooOw_Kg77@TF-
cp{?)Q+_n51~YERYH5kq$<%$LSL36r))C$%5EV(v}EbnU7gjHo%QNc07yHdz>nYp9{_tX2ses0G5dNJ
D#+uEeVq6dDE^^NcV6AQP?91TmZT(!eph&blhH%t@cGcb$Sc6hA?5x7_-~79I*T`*gKZnL(Z%S$o@iO
jVi1JDrZuI-2PU!P%EQZgdUy?vUfC8u96-$cqiiD6BNw8ZbCBzfo3#<U!1V2yA;M4g8+O<-6n4)0ucz
+%^;Jy4L`XY-?RffUMOvXV$hNffe*e)vRfNqgwBsniX+?r*!s}?0bg~+cULN`{T6(^}BwxaK}+fSsf6
E?H>=A%Fr}zIHBwkq?5lk`mpxt80^g7(XeWFxPf)Nf2q(tfL3)f&CU`xKsxSV4=UYjW3m7}i|78y1d-
nAI_WcqCwb>C@*uff*8|Q2Jf{~P$8YtxHz+d82c@XztOwxHi-mXf(`Db@J0KT6&u(9JwmKK@NXwtvyz
m1P-|ML;%?-q%D)^~{gT@gw9AUbMJZI-hVDC&sr>=Aor@`y9#%Dh=IW%*`b|m$m;Lzk?iW1M%YBc-D0
Gp+c-z(bI!@SdH=-jZl@@=n#R9}-@_fN~#+@)ZpfF|$Q335}ITyI4e4cX4`5B-h_y}kEle|+w}*~GPj
k7kO$H*(aiJH4!5T^+n$d_~aiUw(D_0=B0!>#D&(4Z*`!R;5UPXb`@0o90Nczudc5e*DI2c#Z8x^+3B
7LqyGZGdAk~nS;aERdBD5h<La+ibDIB7Z2n6?s(2O)x#th{TEP60|XQR000O8;7OWVP$OLna3BBxFmC
_=8vp<RaA|NaUukZ1WpZv|Y%gVaV`Xr3X>V?GE^v9>J?(Pi#*zQ^6l3gNEoqZj+eut0-N_Ysm+Rf~e&
{5vla#EZKwwBB0s#aANK3O=mAYrh)xE~O!@WtK<oaV~F!&%vZCrJgQ`svLnCa>1>FMtod7d}<7|Ohiv
s8&n$w-vTBC8h5tSUtwgtx&$`bS5X%UFq37FCH9Z$DgIig)iXMOmyxnTdFnXGJOIMYa+_x-OS-x)Ap<
{uVcRocq%_EoG4g$qh6=%5qr*rSt{Cg#YBnT!tl%oQav#;DQ;9WI#R(l0?koL@EQfT*@O=%`}40CK|!
BN{xg9%#%o@St%l!%QO-hHDCEhp64AMX>7wRoyUtjD3mOmXQljDCh^QXNwP3VWc_WifVr8kc~CB$wuN
n{*6N5*k73$nmL<y2C|m|{IuZ+@a6Vg)pieG?k{g%n90{jeUjFfHGJXDP^8AO_@4g?27jamQ#Oo4Cml
Y%NCRQc>iw}~Kcuxz6pFX7U;fNs;?eBmDS>ZFKU;w|6f3D&}u4GzTyk4hwK@vyj^{agl?qs20lvd{-`
DwRf5r<13Xsfcstgd*@Uq|KxPXLzh9Qw%OT&gPR!GS=ng5tKy4J4_;AeTFu;&NJw!e?0id6TrqM*@DR
_cBnpo~Hfu6?{LcUpIgQp`<F64_iXk%X`j`aTY3v>Bx3>vl0B2EQ2U01Jm=nK*<-drbRrfkP<ul(Rh9
mr?;l-8~D7dIpB%^!vj^~9<nP&U)|+CLgto*I5AxAFJ$?Ko(-ncG+4>$ba-@h^yKJ?xCn#!JWC?n3r~
(BITzDdO>gBam`y{N$Uq$nn95L$zZElJf2MIE%c@A>7c5{IE(eA8?^nV2=j$&9WBxt-{GUA7zeAJ>xP
9McDG-q1=Y^cdAE&tcVKNb5JRqPj5^?+$uI>m&y&lmE&2Pt+)9C5v{EMLxlKg-{>IZ~3!ehLFV`4=FO
hcI3h+Yl(9sUrHod`t_U~y#UmBs~D0(pB1gACO0$R$co3&wFIGT3eNB)dQH;zgPj(i@5|`r6w;=iX20
h9|W3diqntq5r2WP6vpfuks`=2fz>6{dATD>Fvp7QOO~$c9;Z8iL*GL6h&4Htg6t{2Z4IIlwt;Jj*KT
Hw(?2L>aH*107g}199kgeLk;6J<(??QgA!Lqk#LG^XIP+lRsi3i*a0;G@*I^_;WHIUlc4kl>8eB^W>p
$4MK(uXj>8f5kSS>tfL)erGX%qfc3D+03IuK?l>)7zd@%_C4!sbt9T0St#<0g>-R2UAAIe6XFi1s^C{
T%Mm{gG@Xh9UkES-&l837znVkN4rXV5J`c9&v27WYe#S|TW<!4R|}@;vD~LJel92h&)>SO5SS0>lUO0
3Kc^(j^T12eKwdSgdG(cnkt`d|q)6QazxrRSuYa9HYXN<5?9az+X4MSt-M`dh)bk_!;d|*qU)Uoz}dl
WHKMwZ=cs6Z-GIN#Z#@ot~|mAxYfH4iWG41uAjojF^_FGXJn)Du5iyoTa*@cLrokb9dKXMzP+xS=*4g
#wc9$4ak*fdtqyFC>-k{w4$>&q_f3oh6Mn5F%o8z5RR#PK0LP$ZRg(zU9iH9Ak&JxX0i;=@MH3wHtAd
SHqBaallvKEc!n2*c;YhEG0|>>n8S68z0j_RzLhRt%2S=?DTS~;X>l<)YsS=GvYCp#IpK0baZ0943!I
=1~`NGAhMyA=uY_1c-NzK=qcUZQUWLPxb+x3SQ_H(m|<tS)kKexb;nm-}FaNbm~%!8qCciY_i*9|qFP
D$uar@qnH+heh5&UyQ-H*|L_SfB;Kz(&Mgz;wsXb|dXHXe{Wy;Rar-sU7#Eg~w;b7M8WuTGLv$)!%ws
YO?E=`de>HOMczfe(!B<S3<Y8-=TH0tvCF(e$XT-$ndGw(7T0Uzkz~38Qa3gZQHn(0j`mJ>_ALVkDcI
VjXd1x&OWfhluQ)ittIMvXV0u-32xKeyV@|EEtqaebiJ`KwpY)tkHwYqv}P)J<+UJr4s1XLC4`=sAE+
>nr&*e;o08{=IAg6xDvDH{=7AAw!9phTE=aAXrtLOYzUko_yVS8Kn*-L^?ldslKQ3pEdRv6;^>lxDm=
lN0*Z=chKt190w`Wuu?f>@I|Jc!C_=`-=7%9KV<o@=b|NXbW{^i@p%@Cd*G{dH`{rAlI?_N;v3ijMVO
X-RI6YEZjC*<P!_j0@E?Ren=YHZ(@R&&M>pqE<;Z6^l3l3_RKzRm}&YZGLb+B;X&uI37;4E_PjK!ilX
uV>-vRmGoHgJEZ$2NUV=d0LR4GS6@gE(=W(!F=K*JG12Q#DiSWeK_~tkPW=CV78tPI-G`O1uhi1jtZW
zfBBrkcvV53+%Es}dzqq_A*69%(bEatp03NPgCmcG7*z$kP<3Y)=-XH+cz?D&E3!Yyu>1}^D;<APgRY
lc4|N{I7?r(W%2ed*oV)vFwo1@M7dPaijnx{QztznMT;CGN-h6CAe(J{W`fzA3tQfnog+F$?k4<;4$J
Jx^;Pa7*71xoU=E8TZ*2d}^!*A|A2Y%GvL<kSXhU0q!4Su+7ai1{+(WUBc5RV*S6D3A^1-SSWuWVBj<
IDa}X;(B-jN{6s$hF}3G{(f4blPG`BMi^3#f_yncqnVX33J$-L2aOV)?EiAm8zum{p}PmRtKyF3=zz-
JFtt0R&nmP$Wq&}L>TWvN^v$h6TkWDw_*+w8(~JW3}DV6^>Z1<^Ef1~^*sl_p|dN9Xum82JB#r+hSj}
(F^0uRe4w)QABcN*5DfVZ#aow+=U$Wg!0Q{H_4fY(f8u(*)j{=LQrqRkAjAd2of`-@@cvW@@9pIB^u_
7rsfV_WclN{g<Ja$AzW3ainu-@Gpd|H@*zjAp9x;5JfD2aun(<0uC~_Ixu?0sm!z2Pw{D=X2O2CeYs<
^p%2~Xc;<;$!}Bbv?44e1yeL_-$#F$bQJ&H<^&WGzTI!AP*&QH61ylEb60I6CdN3f34ti7IX<3zB0x?
?8^CY6blc3GhWQVK5-t$qZ-h&2%YX-~`}%_MGQf2*-I)1S<{yv`N@(Ml9WK+ZqXFIDW!tZ-eeLNlZZO
AfpD84ltezRNBQ5L%$bUvRx2WkW~1q9a(blqWF^Y-6b_lac5xWiTHr*fzXj3oRF>wT+L({REn1#iIpz
w4sxLAI5nnr3+V>gM<R)DCBZe>K2UCy52a1m4iU{g@&z{CDQ+DWM=qxA9XShVtUY|Ttt}>)VBwl#S^*
6@=9!a65aTgs1%yp^DWNlUlG4DioHD(Oi!4PsMbZn?+|)<KrSx0ezHbTi#6855GawNN;E>e6Hhs0+l9
AU|qZc8@*PmyrS)9^Lc24VIL}qf1iw9b9Bs@;*U_K}q5~TxV529~SEY#KU_^az-ckw`P5yG+*8-}-~_
1@Gyq2m^0#X<s46mEj2UP&XU_N`Gv1~>QsvnPlIY&d2V5KIa{s5uBU;bg5{yV^-%DwLIHn9yhWe=rgY
W6X0-Bn+zpwQixcLnB{KQX2dc*~oHz2OOr;-=_)a)M%{-m(c@ih(r+>PNK@kWj2OwQg1krRDo5jsC5}
Mfr$<LCLTcqJcVZH1H-}|Kve;oK@g9G+{-X7(ccBEp&p`Gkv*g~5}2aoY*GI)QceInRYXm9gtJ24#aX
4uu6z*}2M_gBQSO6#lUJ9-VTnse22#B%-O=93@;)nW!Fx>M<sL`x)#c?G0@clUMvu~o)ML6*3rE}W-s
2JhC*k9nvH`D~8`5&D*_s}C4<?CR<@6emjX?zcEO!urZ94W~B&rwWiyMROO&z5swX621K+}iPEV>?|)
qsYe_w=dx+ENZ0*w1dPp=mKU$8>85+*UXn7IifOodzcNWuQ_1i-}ze&*5?3@McC0Y&rvV{0Te1k*EjN
y@roeNlIt!Y65oLxZf|OOi*5;hTbPBb$i@zl3ir%(GWTxQkV^vl}HA=51iAMK{g<{$Q^>zK>7<Gc4tv
kc{y|e*7Rz4ea3vzKA*Kgou%Z!lWs@VFfF5rV~cFNJ;r3Sx|XIVo^C9l?Nc5Fou<-+zVxtLWMu8~`A#
@Vn^doB&!gN&F_fxhZHU=Y3CD9OUGuM1K2WqZRtFFu2&}4Cgs6l2NNcj8_I6-)QAWFuDu4)-Ti9WwIC
wDG4B?uJ1x41h;XamgXta%yn-Vavz*Bl67mE|{jtG+xskPJ^f{qR+><;&B1a$i|_%z*;DKNL@7_`*PG
@ruA`t!<u-X)T0kr6a-5&mkvAh_^`ez#sBXncjgTb_k}MZX`(mhBYpxiy<N7S%0<AQ~*QsnOjYcao{L
uya$RPFYv<TP+VE&`mvoMxu4t!|@Ng0dH+>owIfJNQHeXOd@n=RA}!avhkx;*Q2Gxz6D_EX9#HgCmLt
lAIH9^W;!IrhE6wLH|oZ{UB^mU0AQwLF)l@Bc0}ju#$)*r+^T4dHpQ52r%x&u()QyNT-C6M^IC@2W)=
)I4YLRYdYn3`5H4|=qT#6=;|c3$sleuXr_~hC8=d=$WpoRe?kY#MUq`bj{zWbrxADDwIleZWZZHrb`z
Q^kT>m<lbI$Q<15$C|VmjOk#yB%GxW0OJ{Zs07^TS_ggtgz;fU>J~1Br7+;-@Prw06g9jW*m<z|tE`?
NR_HyeOnhuT507hbx9yiU2l08+k<q)=)*Eoq3fc>)!A_%BdJj3Xpd;mXG!aMNQzgv2MFUoJ~s}f9ja(
uBfkeMvHiX5dv6Du7!6t;z($Z4I?$6GARPs6ZiF?{Vb6yHtZ=DyK82{R{c>AfvM!F^Ry-T3=L8Gna_`
wfSX+?Yz0ddp3tT_<hE-hak373z9gwN*drNti@|2XOoJXTEbK9h#7~oN+RLAE$Xo3XjPm~3I|(A~0~^
enfF`f7QXELh>~_Dz@P?TaxX^W2pXb{S<C|^JOmmoN40mmamVngF+rWSE#KU79DZ9*~US?sJS#uel65
yotUYn#!$~Xt&+UCNPl!JMlVI&9jRwgitI;T=cbd#_WcBkdC%Oc_M{V|;pxw7M7l;G;R1{LIZI7XX5+
RX86Yi~brU-zbO2a}bx5~0xtQ^AA>w{m@w1glvT2oT58&x%MEwJJf<go)A^t7$f$hIsxWHD_uZ&lg&`
kZieP%W)^H%!B}#zr^H9PZMBtnzKL4qV<5ot5km7z@<_1!DdGTmf<Z>MXYpL+je-bvFdn=!X;~cs>11
l58dexyF9v&Md|k`@i!I}122O67E|!m9<y4Yvsa4SG`mm7i!7s1$x<rD^*Fo>P-nr49g9=+zDl8(i>a
McE<tz!GtAbYtmpGMg#7_t-`tr~h$k1;VvuC_7-5$Th1dZETzv)rd`hX(rzOlE1A?F^Wr;&tP#_R6$e
-qMit<5EMzK4)<iu(uB^FPUa8Ww>@#FIg3xki6f%uQ{HP9xK;A^22^2I4u{NDlqqqTYO5?2Negc7rCX
-wxCh)BLeHDo$WZ7CgS#P2v`oh`|eV67!)o}ud%Q=$)4<JvKS?Lj_Da)G?G#m~nv4nmF&X2QC@4!h?i
*c%H{2&FYb>_I(8TiJxl945utr@FRAY0(BaLbH*Rih4>xISU6*yoH>wyaTSItfdSJaOlm!4#&Uvvm5&
C@zqQel$s;;P){>cYmP*AJQ3rs>WxJkxnEXcsF}AF+FW3R6v&>SW*RF}VI3~bU$2*6TTnzb7$pGK#)D
T0;mJxw;deZS5~p;k#5J%uL0J=tmjrpiiDEe8=zQmcYm4>y*==KKxvaJ!o-kiX<y$)20PL1m2?eKMui
{J#sj>vNCM@REyhNAb7EJmhmwsK74!`Kyac3@+CL9d6k4?Q96A?+j{VC-yESnp!Izv6Y;@$OVgpgW$W
hD<>c19csoWW}LkI`BZN|>b8Y9<S{m$)|Q3owSZ5D#M$T<=|_B(#n6tL>K`Lxt+WiOdeHx^N=^B*5>3
`b>#VFX|ZI7)?PiWK0PTW<(>GXcYA!aQ6~KHVSMkga8O&Wi2xXhl6l6Ri>P5ENx)eyI;DSyS8dEeF@;
Sx?+uFsz_90<&+gh7KxgYp2p`sSaX>MOxWb&^z2BqtGEQe4D`A_O6TN4b*kw@k^IBZ^s7&zDaK-tpFQ
iREi_rXbj>pqy{I%bf%=Gt1kzQK4-hMrvL=<gEx8;9)FhrE=+5-(9W#B!lfzSY8XDT-Vr<ID#(MU6_L
gIpG(l|dOwtqra=<!UHTljLuS{AL_B5DKwBs|?0MQ_3KtjU$IT{D}7^B5=pC(y=R0xW28Q;Mh2ac@+S
_ToACsCv=Z&T8t$huqOVUbR9n<|vtwJYQuiM(KylNR#D;Po6k+bD}ZTG^qOOPnAjj7EIYk>qC#KuH>+
9Z{7TCIQ$Q;JkdgwsvP@k0J?i1b=8*$cp-AV0V#~U@A?q@vabVPmxih*QF-Ck<bI!{wki4>6OGGW-Eq
f4PX;CROz4aj9R@^y<?J;c18rwbiN&AsXP%cvIvM2#syf>VCC^4?>aHtb1u9p(cjkVqz{F^JpJ+g`Rm
Kc^wsIbt6JBXH8^SJQXLJ`KE(5ylSFtZ56Sl7{7qMKfe~$NC~T|aTnRRAK~qwuro^dRiUCgfk}R+wZG
;2rJdp#5eFlB#Ro8a0NP_hYvphCVc<)%vGe$L8c9iAg(R(v3GLJgV91{AmnldJxRzy#tB?=V^4}knr^
o_6DKo*06mUxi2%Hya91k9;x7CxnN3E-s)WwPJtMux*emi8E^Pxc9lDQ`sF&<^pMPsWGE&zmhs2IRDp
&GvY+^?c6v4SK1G<#laKWz^)%QD@J%@f}B*e9#VGzcz9828c;5Q|gi}lJlf(D2_y)BTzB0#i#^IE9$P
U`PB|x^LnRVX{9L@A8{ph&O+Z2f_hkG5F;&da)O>33U^Mj?$WS)`$7*<=y#*ElC~JzL7d-Z8-pNdlb0
P!6Zq?|wKS{SaWNUVo!3eu=ZlwAZBR&3RQE+(N<Q_E`m^8V<bv5Us|C~wjVdmHY?MZ}T}!iMzuvKAm#
-!l6LEI>{D;%;Cl}(yd%FAP?dj$7R|4J%WJ-Ac^8Ec<`hGt7w-2w+CvPY3E-&0gd-?j!#1~q3(z;f8M
2?k9BeS$40iFZydT!(bs?7mkyhrhOA7izM{1~jzTX3Q2qF+qf6_QdQ|KdV25(TS)nbSziJC_cu{D+h*
-5VjJW4fY-kGDI?HPmLxedp1&D&F;By4V6g1wkE>)f6NP5Ub^KMJxte0F6tsZ!@y26gQ%N&G57Q2tXE
iZA*{JSBH+FH*HJTTa#;%mGvzPY*2BKKvgP7gCXsmFV|Tz*1&#k{Ef&{Y#*qD41)vR?qlORlQ5lz*$R
jft1NA~(e1Z8y=eQ{y3=(pqAs80!t9l;5O9Qy<4aF~rC}Q!A0IV{O>cBZwG6)g%{O54hmkz=pN^(;e?
U-t_4TiQ{hLGo=>_&ZaDo280q2MQ({%Bj*x{TgGzF$gr&%$eFLn76u7XE*OVPIT+7{VMm=x$#Rx*6FB
4ou!yi8mFn=t?=nBghDdN0XF0t280EkFmE1O$d-!AYe+r2?6QrLlCOhiY0A=9U}8aByXjzcv?O4Lqj2
H*_+PI%RK#Ni%U^JX-=ZvW%qaa%bK`J|MJGgI3I+&p+bL3%yj`6a62|J@ef1;3mZ+I>Q`p#YS#DH#=Z
Z>w~J(4jm?{M``oZ#>xVRkUj`EmTj<U+ez-OUDnP$^px_Qt-(D_by4%7C4D({s!t4rAt+ZZH_chGF+(
;gion$A#YWAsb3hYo6`$k9Ztt@4JNbqjszLYgXN}hH>sn-V)Hx%f6P)Oeacy_w5GaZ3N7eQ^hsH449N
L@bW;}?Dob2PA_v`+9Yjh&cHgd12^KBk)Z?$iKZRxNv1)nje%3J)<d^y+Ujr6<u>XV9^jHAPFcb*H@_
SqC>i-CIB0<e2Fb<eF+xX`Vj(U-_LSnetT?u_Fb4ag-_?*6GyNOU;G-mF4L=r%4?DngjPn7lmw@aA$l
`NQSp{N3rBH-DVIJ$(m8<csO#{QUhnjqQ0q9ihFfcZGXAh3$roS}UJr3l)Q|f)s{9)ycj*231g%q7BE
acLYu1R?wa<%MxeWq(o;@yD<XqC$w=Z(hbG~!1|N<QCTDB9&V<KA2FN&+T2)+m{xG`*XPvqy^DHRPb}
JRc_Nd#$KGS4NTjeT3WVGkMLDD})OnzO^<X$aT4k7=%29!wH+W9*n{R%5GbMjZ+}zX)Jk|?*bJG$nct
6=vhPT?L!v)jv4;L@Xx3g+C!;*k1@44+v8?9PYTy~CrVcv$9vmdoxw|UWpTb2Z4O@gsQq}?@?ZMlWQt
-q$u&ao>1>RXklD(%4yw6CD91*<Is4=O>^l~@lk$&Q+s-g{K`7Jg~pa3+&jlH0F~UeGZvgIj5RLMpq4
eMceOo{F!&{R%{Xf6+W}rLzto7<yp*5imjf53}$Ev?6pySfNhQu~^-rEk6ThyG8LqsOWKfpmk9h;a<u
E4w{e01jr;hOp1R0!TDWhh+%I&@(eNl`klfgUC4=(n$6Lkoz`nU)oVWGvlX{;4Ynonxw)E^INuG<zIi
@<JGr=^*a4-+#o7Cd*MBfKH844!3rv_tU{144p(9~f`qntD3F4x}=$R>{m#pAyl94$EPZBKjDa7B$X_
Vb7I+I*T2UJC5=Yk2{A=U{Vb5pAkCv*pH{Iiu~V8<aPTwrMdEQ?71<2cOG(U`$18u7&!>5daDAm%$%Z
8(Ocv;&PVQ3M|Y6G|YR#uEL)psWw<X#jZPU4}&@fk@>&^r1y6<2xr*TNbT5rYv<%G)}&=K(#!f(2_VU
d9(0|!dBT(kS_YIxjj+|JB`G&9vr+Y{xmR%HS320yi;WVMJjWTup4i%ajR-|PM7oK$aMp6j0Z%gUdt8
2A3pLq;&Xo*KLF;VEkk!#f|Sp@^}zaCFY46=O4QCUZc=qU?iT9$%xUKiv58YM{yQ=tTKkh~ky+K&0u>
9y>M!)tTm-4_Z1&IKw|iYIyU_cL6UV7$bDS^#tF3dk5a|GFF(A_@&sgA{G-Kr*p40$PZx0wGDAbhw>J
zUj=i}eDs;Nzt(24GQ)uXt*>kcdEyCJa1?I6L{T~xC4>U*+%^!>o8Q-dGm+BMkPKPCc@sDZ})3WjiwB
I_Mzz_baZRJ-Ni{e>=eg_Xt1-xm`9)z2C$bH-<R`|#VD8=EGXy^H(D$@zCMS~Ca*XiV|&lD;t+hKbdL
GNIAStQhD%EuWto>N`#c9@itIj3k@wpOt4YA6fV(=0nGgM`AK()&9HIvpSJ}F3|zsZB{o-zshtTr`fo
mo@4Te_g$jWJjma@`JvAS)JK;KeLaF{>)RKu1SAD#dt`;%9gv2lYel;v5O?TUZ5ptP;GS<II5}y)(6N
e^++1?47#(*&$8rVB+GDVxjkKc7+f3R^H+1Eqai~Cg-^D@iwOWHY;%^VBjmNM@LkYC6pTJT?SXj7$fA
KbFk4`{%ElX&hA?!@0FU)l5WDD*CRUa%z^K4^@z1?Xe>ihP|yP><XIkjrJ$<0T!?YYOE386{Y+Y0I-8
cVuuQ^y$Oy+<u9ZckO6Ey0M9PD8d&wK3JwOq@@izdwJ$kpLuIeYwRB&O6kYT{g}y)tmc`Tm<17cNa-0
9g=(W=8g=2v0dtMT@;2Lf3cnZf3&Etxe7?wnL13ZFF+y(9RFT~j&k$uIU#!Mc$B7x)lK=X)OU1qY6o1
kjKiD2_Wa_WwnKvQoXYtVE}$;3Vz&>lo$#Uj(F_=Nj&|FdC(d|L4`dK?qt-!8u_GMn9B6s?CLlc^m>{
7s&bohvV$}NM5_?YT8N8>?;cdji@4jhVSm@mC@1Qj5`I8te)4{YZ*SX|Nck5#0J@UBSO)DVplVo9!Xw
v)0oYr($UrTw~SKA&|`~npchFrT8`>cQtM6E8FxxTdbaN*pmYros~mu*}^P!iH1KVLcX<@I5Q@OosxM
H%q919Rw2eEn<xtC3UukIxM*eImYzpCYBEL;ISxc>eXUE$dxo+{sj5+fz&W8gnZI5N7}8#vEz_Lg<Aq
DBE?AclSLrwiFG^{z6GrgL6rTE7m2|7NX}J0YjFtxe7}cUOi{cIDRA31?K%ELfLsYpFwqOMm*q{J>Pv
#*ME8=gI~mld2I?!fBhUAlvG8E4|a)!PcMvH#VWLa)`-fLrYio~xg*|8Y>GjnO0mJ|v>ccT47bl3&&^
DR4rkMq{5+io|KP*5I|7%!Y;@zT2+C5f@=}Rj;}vhFqGBUet<b2XPN<ViWSUC(E4-?K;lLWK;&N}2rG
=8$KQP`~j&VgDW$MF0*NhrEGA234<}A$m68^5Rn|o#>=o5KN7lYi^2p%p_#Xo4Jxx9Tz!M!9x@N$X4r
nR)&Vds{2V%mdbbnms&MrzHy59e==#RfSaeE%pwzL-`;(!L~emuZMU51x@s`H~-dhtXYJu6G@dw0CN$
EFpD$nPo4e%s)ZYnB!7wdt8M4c1+OoO{pK_RfUIE@UktsKNo!Z<qnBbScJx9h7OU;A9E)1uvq_#7Rnq
VXQc6rhsK!j+!68b(L+EgV_#}QG!jtmu`&^;HtiNgkS}|~>9~n9!GiW9c^#<Z@WwP6L*kLT7)D4QxO}
$etv>IlSkqsxfjz7b;h~RXWC&Pwctbx0{+q|+dJv{+2wlx1o@({??a9~vm;RSeO{NeN3RE<08a!=#oh
|Hf>zsJYvdq=-vuDWA`8p5$ID013XNvCVeO6|99I9tERmb)6K6?TxFT(WaxQEC1!V1;cBmWCfO9KQH0
00080N_cQS|<Rbr|19x08{}002KfL0B~t=FJEbHbY*gGVQepLVQFqIaCtqD!D_=W42JK13X#(aoqZW>
3v9=o#&+4Ql;S2zB5-UWDI0nFxhbs>NJ!$>$3IA!!B(a`0?k~+;FHw$@Xbag$K;&raez5eeuy$^d*2)
`hX*w|9^nnXO2!>Lz5``z9n@%==4T>>nk=X&zu3c21WM|mD_KiI&`yX=!KP^S$qH(e5}XkP2NcX*CEM
i4yxW?ODiQmht`yLtMM}B{MTE(WwGCk;o0hZh${cv*7??Pa>Vg`cpI%@54REW&#e;g`Pn8{|iu$EesK
;!wa;a0jnREJ+$c%DD5wu0}eYhF4bN^6F0|XQR000O8;7OWV;5N`Z-w6N!b{qfz8UO$QaA|NaUukZ1W
pZv|Y%g$maB^>IWn*+MaCy~P-*4PF4t}4%LgzkY49qwU?uyF}Fg@&IySM<|y<l5lAA(?@vE>;x9?K`m
NsXfa`;nAnOY@`KeY~PTVw<E$iv0LVk%vxc%Ow41<hJOoY-a9}DHDD(gPGM@9ayQFMwC{n)_5h>@`I>
s-!;OC*rAi{E`0s59Tx1pG<L!M)1e-3W;0o%#o}3L18+96trdH_X7j%<*v(D8nlbq2^{qNI;MYtvMz{
~ONGH2u^DNp*=~z-SZbp^av1HNl@`>-jyF!cq_EL+3XzdutUHi-%S^YkJicQGY3Ju;D;&UmwBm;Bu>#
jAHHx0*6@3dBW;a`*0`{7=zPmsEwdf9|Ej1&1)8Us#U63Nebf%{~pfPyPKVK+JsU{;BmZKT;Wum>AeZ
;aJ*wf(fhoypnqE!!&9xXfx{d)+b#&Oj(_DNu01P%~$|tr&zikG@JP4hsebb5`R%z$23_1Et(AeBe)F
(+!=AYtwPNpZ6_#Evk)Cy)MP30$)q3^ssWKz$N&Zc%(2=yDvT|*<RLPuxwnaz#_=d4NB&R!GLo=3(Fy
EY#r6C+q>*kDqFCJ%%>6`vMsLKR`_eV7v)p*jsnXbXCdrH@hS=%eR1pb2GSwAH#h%WjqUJ&8}PVbsXQ
eEk_!pwz?6Rke>UhlJ<cdsqnXnX9$gZ%EPD?QF}oKmO%SVPBZ?VG-E$3wp}LIIO5J5k_HS%0Faa+$I?
@YRs$%!=?imVz-BM5;|BL;mS}__){v8BwBQtw$+AGV%=dO{Zw9UXwCrVjMQ5B<sG%?`GdsR}GF;%;u+
~+HEF1*o9NaZ&TkWc|aiE2nYsD1=-`qisO&Bk8Dl@?JV*c{s8Tpk3%1E^xlf?V!);CCwaDE*j523Ywb
nAxkosW54@Y9n^M8~}|gSPyD%!4$mKFA~0U=D;{unI|43z~^u!$=M>24v~gU_VvEFY;y9InuKx4h;+y
Z#lmYSFibLreUh2Jqu{n!$V{})Qmd9wEEXEuodQR+9|r*HItN{3bN{qN$$W9Lo)(DK&jM{kWx%vjb}G
L-G!gxTik&(ekR(8pG*~h7v{v&`h3e{5Jk+GG0NCqR*`qZOc*9$gp9(~C-0+jZlkRw(eF^pZl~qa@vc
|hkaE*~~v1INCyN7=8Ypz&!WTF)k3yfWb2Dt(&@R%0Q70iLYt%@v4UI;7+Y6{^6>@wAf_9%4=C;%vLD
3f*8+j@DM<v82xRpMCJIZRlGp<f{Mnt2Tao>%icAEl|NHiqC4#Jyqx^Kzcix25}*IhBcSoKYrtqmQo$
4{9Jq>IECV<OcG4=#8aT^=;!t{}8?>a9Bprx)rF}s&+{YkNaKo#tiVG<gVknb;#*0jrbV>=Y+`1WviC
(dFkvIjGP1((hK$)lIV@7u2TlYp#*+`<-j=(fLNBjW-oiu(jrbt8Z3-wS%LJk<lvz<5%nmDYRR_^z=Z
}}YHPV8425L~Y3Efx_8G#(6TphM0;9|-9D?)Q4}8oAID=$o2T=m20P+Lq?Ckd1fj6RGUYxD3Z#50bM#
-119mdS#Lo}sRp!=S7Be3{c8ps8PaXKDxN$E)8ai5WH2w`m1J%7d)4V{;&OcfplwPqi6FMJ_Gyh;6Hl
)mHxrNIoxGXH<c3besMqTKullK`gIm#^nkv8qzKSU_VQxShwTcsNScWB%Rg_vL*@0~|LIsm_biz+IW@
Ep{1UDs)8z7Hkl9;Z-rm-{MM^W509Am#BpXz!X6fR;&~=3O6twZD0iDFVLh{*u0K#02tuzhVviRo`n`
QC;^TGJ{GeH*8r~?%n-&B;vf(~c*j_e4EVR`85v{lATzoTjz<~@OxuJ;U=TpGdEeM{y9;mN7g*(>h<n
s%%Y*qVwzsx3tLy7ZnzA=AjcM=|O7E`iHK5GW`?j3cUzW&cmf-9Xk}tHxL@&2u3CRIi6xH?3&F#(W>m
QDm*ny>fTa@Z>4GHIH{TfbsfYR5uZ{GYcwP)I4*j;BS`1**-C5V@Nf#9dj3#a;`mT*$RMww?*a9RG>G
-<mcr94!@kGP#UDd3C-hkYoar&hg;MeexqPGL`{1@E?u8>n%60c?_1LOVTS!+9o*%L%W&N3pus_|DsK
!xw#k20_trf?Pr~e+Zo%IY!izO?$=OIl2@#?`hu=_h}W2`A1~KxQmtrZc1VZRE|hHm~g!f(-!(ewvm|
#FmQM;V`>nI-MNX+w+71_VUxGRs64`{2U>T2!flRBz#jGocR-1{H)uK*qktNf4G<4-M;v;X41&&skr}
IbCEcOcv;FB<CO(U@cS|EU`lE*j5qJ}O!~Fdc#uE8Mewe<)3inSVcwAz9Uy>%7t_4=?A?l^K>wmm1Zj
0C1V|vy&8X+*qCY{2q1SfC4+H71kZ#LOv;Om9r_uaDy!^PuZD9P5%GNN9NyNCKebLPVe^Kc5)vmIy)s
ipW904@)x`kS(zjq;Ojhi<|KqNevlXR7?t_JG_&K=*LQ$6@VHlnhaKw@<*}xXF&;;9YBa?Hw8qj=qmV
_pp;OPb?CWGm_~rvTnzT_JJH60>&hEEs<R8H*_bu0x;}J3=v-mP%%}DgVsw_%Mqq;-UZJ6m|TYg-H5)
#t%y~?ilak5XPmC^s12+J<Hp~ud8su^3D4;7V~mW)cZfkMKRu3q<H9qYV8`Jc-z#vV+I4nkF9uRXjWX
qem;2;ihR$PKI?YHT4=}{tp1;0zSISB!3b02ZyeT@Xhm_$S-L=l6->3QLZi~;{Eu$ZF4|JY3e|HZ5Jd
aT>YfL88zvV!t+!4zqCGvg6zC=%d(_gdHT<#!*e0M1i2%i>Ge6|kIm&fvSYkFQOy0^i5SWmj?^t__KC
Okj^Jc91SSfjy-GsE~Uf}=`S$f6wt4KV-#hD`%(U@yG2o~gvM>FjJP*iXpki8WtQsd-=mJA}=$Et?*W
&)+egUiK2o7w1zW-DsRv`JmE)i`VO5s3lld{&vB`A><(`X*|OVgTE@6?~#!(Kfs4@0~ej^V~X$*jlzG
hYH{60Q7__=W?CM5iDDb?a!a}vp&T7$5?~p?6tR8b+(toi6(VY_#F^n&0~URNTrI;%#!c=xpOxc29?O
~F8kB3#o%mKZ(hlfm*!tw!(yD|pA;}OU>u~g{6%Z6QkC7G7MmYTnQF%IxMsO>~X%PqNS%)|P>3J5Wpz
9c=<xV2Q3I5W!-E*9YMjm9twNEG<N8>nwnm6P$@jN^S$(jy-P=I{Mr~R6`^3UnUsN|MhU!XNJKRAdFp
Z>jJoC%AmtH|IYY59EiKTt~p1QY-O00;o!Nt#*-^D)Hq3IG6pAOHX)0001RX>c!JX>N37a&BR4FLPyV
W?yf0bYx+4Wn^DtXk}w-E^v9J8EbFb$nm>=#g;}9s-+3X2+%?(ua_pyU2tg<#J&WGVGt{FX>Ck#+1;g
OHSmA$%sxmiMJLWxA8c_sGdu5>__h^Nlagwt`IarXeXhEu&_dM8A8e@F)O_t9zbMi8@3pwT=FPQ#6s>
NlR6Qx7(w6Fte^h(5sHE89m9(g-QcMxvb77Axgx<G6*S~z;>=W{W)-_$%EFmv>p%e11)m${RURaElw`
qRMno>x(w78+jSbEE(0w_=Dqka4V3?mPr%6`djA0i-mu}KTjC{Z(y`->D^`vB;c%A2nBkW3Y{We<RAc
Behy1$-Y1%p1)lC?Vxd$?kxGx@KTK>EYk-=H`Vzd>GG)&+-Z%d*t`_^p!cBL*6n?(QqE&n(4e`742%B
v*wmd(QH|xXHiATYLzO6tbs=JR<f%1hI4=X9!{BLO~KS0m4@k^kT*a^jg9u6x99d`4yn@|ZZ5<YeA8o
mdj0n0yHDp2gM%1y-wHVGnT!_%J}C2=DGdm>qM$~WO2}MqxXOW2@(8HC-iRhyEFZqU;x&Wt(QNB)r{x
z~09U!*wmH5|NU>qXO^y+li(SKHLL_TzfO?qjma8I^=j_e`)cb$a2CQG64TiL`*lSo1mv1egeajlvNt
TyfqCkuM)7jZ?B<r(GihscLn#LvFtL$$8gINT;F7xRm1#P`CXK|i4bj$J_pcdd+Bu7Om4a87n^D@3+`
xQ}IF3Isv_<v>ifYW@v*N|Z{{0;^zz~$nld5L&%?lN1dHuUuLS=^&6(+#^T`862KAxNe>*%&;}2?RT2
18{g?Cgw`u|ACKQUjM~%6-Chti$`cfUZ1}s;00UoL%_p?rv;$~H(eO`Uujc<<%!-f4|#fWdUAa7^!W7
j;_0*1>9f_z)6XQ<lJXiUe6|elHjp|9SELa@ylc_ItR(9_5jBRmOJs_OilBFZ0G590`5eoAAWa(Jc=1
!`Z*lZFN=WqAlatlSNwh@cncR+XUA;i}IY$#(l^A7$Uvi!2G30{^9GQZTp$iTAd@C9Uj~@g}tsksRIk
*J41na~VnDy)Z9H4O+3=V)mYKtD|h+N1$s=gMqG^%EITxry%!R!HfHDawl{l-160H$9cal`?F2_#Pob
cF;=V1eT1oZMUh4!R7eginy6RtJ~tIB+6b*2Hr>Cd9-Ah?+&6u8#j6EwR}3K!@}u(t?oK5TvNOxJL{5
Vs`~=A-}vkKa)~`v>$2RG57s9wm09FhgTgzGHPpHa9!_>4@*qyU=>Rc-8Ug{P%yG%q!i5)O?I@=V9FU
<3~wQ#(`ZICvQa-lb}>#MG1Hot=>cYoO^G@Exs{+usrS9#f<cU0!_<Qx7dVi!Q><+KZqXxwb-kZ=Qko
Qw`Qb3g3{~Iepod=#^f8g3yPz;2{D$5_mx9553=$%N(ucV5YIvlzWVGC;KD6-z$R<CG!YPp7NfCw%AV
m<(I=B96DDdVF5NV;w^BvV6By&VwGN?ma-Y}<$hJmaQ%b;{{myNM>7{vqc;JjfPA6<SqmhozEXf#Z2o
GuRtjcrMeN0*F6o=5(Pm@4@QalKcK*$lLJHMp7T-E0hDGV0?zFHE^d<aK4k%vj1foXK;bZ5vCxNn9AN
1?XK8MQ^d5f5YGUOf)C`*v{75;i@gY0gFP90j7m=2rNOfW6TVh)bzRg>3!42DE4_7Fox_pVQ9Jh9!qb
<&hzjDv|&4+GGql)3*Ko;FLryRQ`ngSN?ns{F(OAd5TDQ%lv5F*$%4Ekd!if~0tzn+2xtiOLA^uo^+*
W^X?!yO8psSrZ;HArnGp)I9Z`aC{X`K)l_{B;0duz5fc}!~q|gR<LI&>)Q)>j&q80IVEeT(aVs8~VYd
SO?%Lz^p2&=&B2gv(DWHVQ}@>O=*R@wRmB?Wq=9C%XMh3xQ|!SF{x@hXd>1Us8mG}fIdu?PM5yvnh<R
-t26=}vM;KFCksrjE!Tl=UNW?u(ueLsMdoRm%!q@xoctP6a!xbPf5^DLtVgKs)AYFd)F+;^b#qO$lg?
=u@e&Lplit+vrs(dRH<V(L>I34S=ivQ(^uEZ8l*QSXGCY*vh;3dDsouF7o&GT0%*C4=re`Ej4IrO=h#
*J=@ubQGbb(wCgWTax=5}YMdzC2pDn)KAjia65OPUzCL1zi<kH0*o<03k%c*zJw)|;(_=jH1IT2&z!;
4#*C6lJ<s}q2rmrs7&`n+0xBU?UT)C%#6<0ru@L@lSi-l=K;hAalbGxlL>|jAD_TGE)9MujN)Q}k%P8
FCAz@6wV3?{g@S&?W4A6P7}z8d!dmhT<MXraq%$ynpw0qy$(Y4G#^uzVp%*On&aW!F5wpX0)AXkuqMu
rhDJ+adQIA9vOrL!(c4^YiPDs@!3+5{6A<<M!ry7<AS`)WfWZk*6R$nJK3Lh!jXq0gDPyus(8u)x{Q=
(v&?2-I6N^)V)dHp3g0G(J-$g)y7*18n22LHbDf`-O|A=h=?8ap?;|jGCr_UHWh&$^A#(Fq~YuccWdY
3GfSa(nVL5oC*O64o{x$M#%)8v&9K;wnBo|ro=KLOx2b1Vju!;JU`V!wa)dheg~0lQTNkZHi=qUVmpD
<Z`YmQ^#uT-9s0}|NZ<sdf4mV|}cg1W{HHxpn#Xt~Lb-!Iyh6GIPH~Fx%%ffwKY76|}!;bI4tsKvp`#
-$!(^B4u+^qO)DO)&SwCumfWD3d?yL?ZZ8&+noDC8=v@%=odx@%m6IOp*z3P-?Vd7)CL+i;_o%`Wo>n
GWwyChy=c(sHRqIiTry$c(?6cVj8tMl%adbfDSL5Lx&*Qfnw&HhK2?#lI%2L*XrXX*(;+Ns9mS@MUaV
dYOi&HWsTXAqa=CF+Ug-{E(n!9OC-jcE3!+)aoO{c3XKZu6beg@)s+P+p>hK8@CDk_7q`(YN%`VFn)X
-cVrl>E=YR-zvsWayh_5byGkap7&HPdDnoM6lA!U8447}?G0RJ@;u)M7HP6sJ<Uby|o<|b4I>K#dTC#
O_9Y=44Lkv<zCAy}J!p+Lq_Pvi9S#kP1ygeNJmWvsUfmFdy9Wzvxi$k72ScW|jTmM(&&nikL7tCS5K_
59lw%CFHIF>P^Ps=DUK3iRFaLru$34hhW@;9lb|Frkc-O+mtR-`$A*|5Y^^{z2HtZ_0m8;idFhCI0SZ
y<XPEumfBW@MDP#vtS$6J-yn6e?!`ny%?!Wb&tMf*8CWr8QuAo~Z-LgW!w-Cc}&rS~J0>F`M(S#YBfL
WueXwvsU~=1%0yI=r?K5cjHptwuI(sFvJ_a<+hktlKrQH8n#C_Eo^@Vg-75()`D$zjNPQfBuO-^g8Bh
gW!yAy+^Q1kK)1zVc7uLMceIAah~Tewc9DTA0+_LXKR^4Bzj*%Q*R%ZP>kl}710_+}?WNl)B01qsz?D
=Xd8^G@CTzwANB!}(Y!pGx^+Re?(_0zGQ|m)N8M$of=EHCO^mK5Cd3J#W)fb%%*LmMAX?=do!g3b(t9
ai^rTxjMiytS??C>{{M(pC?cdq|}lck+5MkE6N&q6)=`aD1%)|agRc|HZ7)|}Sii1VHPH|cvwA0ESql
7wMC(e0=WUyY<O33W$h1Fc~knZy|)CSYAHY4$b35j<KEY((#ui~j*oO9KQH000080N_cQTC87-bG{1z
0L&`@03HAU0B~t=FJEbHbY*gGVQepVXk}$=Ut)D>Y-D9}E^v9>8f$Od#_{|8iZzWOJcMFxBX-&YE<kI
`fdMBDWGDR~2*irqyJN&7X)Y;QG4kI#GyCL{l;pPQhZ4|(yF0V<e(W-eqIX?>5VG%h-*jvTKbJ#U6=l
6=HwPgq$#z|HWN&KO^Qt-%ABVCNM^X1OjiP9^Dvxc`^{i_4dw?;ojZ9nKAIxhf%zyGQ^kuaooc(Q!+v
u4$z3BL5B@*_wlzqb9wSC#tyh_-Ip{>M9!L((YX4j%FnhtizuQ=|SB2H-#<-Bg{GUrwKyU1#O1dOAhY
tc!-d>1~w#FAED18DK98cmq~$0w<*fqbAg%{hqE0R9st_!39vmWofgASPw75rMrfE1{_WrItgB^Fqzc
;W~<*7rf^N6GF>d*^48ABy2DGj1-y`Al|OL9Qv^k9IB=OwWn2CUm0v~;r~0965bKdbBmi66in=<WMX4
58qyTDqJ94KyNBb*L{au=J9Eg)+!vs$#GdE3bI8=p9I8%y#2*+SM{ybr{bmlB>^IduWI)ThfaMvCE`u
CPnVa<j%%l^b-Y#JWE)UtRoab7BO3@E(-!zrXh(m+s$gf1^P3D#0b;i5ByaU&8*>+7Xr00ZHmAT<%P_
WPzX*Pf#;QbYdDu-}1D`*8abk5;1(qw&;!Pp$Yb#7O}zpE9BS#)e`Vpa;S@s`HojN(O>tyil|?Dv3U*
JPc5wVg=w=GcNn<1UKN`N{83PX3mq7vHQ;+}opXPGBHPaP^xXetLIy`ttAZPXXCKP{3zG4pk4hD4v~T
lsliA$AyZ2b2AsK)v6FXmgP;|b1*bZV=OleoO;bpzGs)9watpb1M&Hl03jU9T3|5m55PA3!lh_uRnuH
aR+U$R@tPT2>570iE${e|0pbr1qHjRhofIiMP4_8ei{|86`qXSje><?8t|lsCUxr|B95PKT*K5OuJTw
D%7Fl1cfj@3$TqapfIXhGP7`A|cDI8NfuuDNsj4lNnaFy6nLot_9fNj(b=BbaM<{GmhELDOicQjl|6#
^6i9;dH)CB@3egv(_!bU8WW2#X0u4$EV9BUn>cw<^xCpHF{gFJ3%hHl%f4$_@9Xom6g+S$hl4_8T~k3
wgdqK6Hc7lJ^ClLCQBl3k>Uc<n<RSL*pN-6M#cKQ)YY!YLofTagU45$h<<eYsJp!9&$b^UP2rZ5Zr3A
{1!7eWJOReVpAE22uo0V!;!4~Ap99tO2)5wS*hv-<P-3^CR`A5Sz+9*FjmHDAqt6(V~j8z@e|kugZj%
DqB9}iT518si6-npHsaZ*-i$IkvSD7(xFIz9+x+_SJ%cUst7hm^_NpPOXjgC1P*)W4Ap|$zFT^Its_8
f=y3n3r7PC=m;R1iN#v05AUSwv0&g>EjH7MC2l)@W^Z!<#1EP=?Qh%IyKeI4TW5ZNgZkT;BCvAjSCyU
vV69CFAxNkHn_$uV@l2ZavAOJkQ@g1w1PJ>?(6O<R>cjA^SYXVU>ft|yU7MF6F`cj!JhC2ml7%1u{O@
{|*!lxYdFc#jub*HRE0uMXBO4iPqt<YV_lN5Imc>3Dam&Al*X0V0R2j1c5fo-d=jX>U`WKXy08f%Rq(
EF~(B*wiw)UQ`SSJw)V31r_Kp0y-5~tgxlO8;X_c7qnd5z?zoY9?EO+Ff5`4Grtp;R;xu~R0{#6+}&n
PO+?SCRPTn^U8V68Ky0*Fb$><m6A(A)!H5)^1jR;?BIpKIl4-=cUrf<(X}Q~Py>>DWk=_u>HG8xTNbq
c*gOSfRR`JM9cM(le7$0i!sRdI5Q^FdW5k_XmK9Bc$)cujLC_uIckNT|0gZU`2(~2AH!GQVsrYsJcH(
wY@z^Fq<eQl4H0l#A$F>UO;0QF?-!Hxy#FS@a~{#?m=#M~uTP0XBRO(Seb&w#uEO_C%M&Kk)qKtbkrM
(%hH8}c~%v6K=^haWYb6MaOW4ZZJf9gc7>piQri=gH8KfKCg7vj`8X+ykOrq~|A;Y}n^{?0-b}aR;c^
OM+tGJL;pS>9c4}p%4>FDXFZib1||;dweo6rOC#D@(oK2_F-73@?J<Pn7{q@3A5<Ii9$m{MFL5YXDd4
PsTvqV-~A~K5`R1NRFI*MsX-MyH<U-zh(@VSb~dV;gXI@$c3(A@;JZuHwn5Mc#|1I2vw4%6N@yK)v1<
A@73Ediw$l#Dnw`s*YI%Zz7>ygXYUaQzA)$pylXrc&<2eSb$j}!dn5{oCOR<RXMpJ`#2NSUq;mD}py+
7?bpa&v^=WMD`Pj7fvgKv$kL2-{R_m!kmOZ-E$Z{S}qD)<bHM@>c=kBTs$sHK!SQCy~g(ng}iR)|)r?
$Q-4u3U-HMxQ_ZtIm35f1u5kp@{n0vFsu}2-_JaHfUubaBUp&ka%{PjEye|tSw=aV%s{lw=+7hHfy_X
q)>c<s===ioZPf}<A<GVt^@tg*Z`@$_jF#O*a^APyVJGPFY}83P@CSnV_*^-Ci4ICIPpJ;3S?TN6SVl
Mtc$I7O%kv<aC36@N?eqe-wol|Aca1W9jnFzvsuB~{L)H=XwrD;?E*23re~~SGLKL6W?wgST6J=w@SP
}psNmY&Zh-L&l(Us{eitQE37BUc5<1rAe@rK#`xD5V9ygh16lms-%jb#4ZMXA*(>z+W+o`ta*H3L{J8
x3+;Aqap))+N)5z~cZ!Hj#VdnKZn_&=4$R2GYJP<J0wIou-yx=P5}TS7_eMk6x-_9TT?4>jJ)i6V33O
Z<<+$2LfQljS2P-i|ZpWbwUnU9bGW=}A%5o<SqwB&|E<yE@<zR3T(<)MJ2tYsxzI%K(RZ3_MBWjt)Ge
OBm$lJ)yQYNQ;D!uIM^9JvP_=y2KGV1<|pQ&Z*`D<I7HP>;~0|j!N_!Tgz@CB1-5@w_g>oJ%9H6#dcE
gndffLbV8b+SF*SZmJT)#;!{!Xf#G<4U*rk-kKWtUX=~QHjtMK}F<VrySRs$2o2t1^&E@h;QRR_wcZ#
w_wy%oiI@{5Am)K{99g9#{V_FoN#{_Rja$bMk<1r<#Z~Ft1L;VKSCA*<YeXlcT%1b4SzRbjmPDe8;UB
`i9q3qXJZ!-wyPs|oey5Rc6-LHbzEnmLI9#xAW^Z@}-hpCYjo((k`feO`Wd#h;D>h=nbnZu0Wo_B0Vj
{1b@tECK#Hs3}qC=yI_ydmtA->5`6bMQY=i#<^fEq>BL3T!Up=r!4`+6&p$ty|eGaq4a6pM{SvEbYb1
#(u&wd#$Sq^rcgAocu2yC6JAIx6Z+#f%>v%?!=(NgUMz$ccIoFc+cdJ=Ry?vke!fmua55@fI@{23qQF
J(@yN<8tUTwB7q;%h%1ilot;c4_HE&Vc&3`jys0X6`l!DD5i*EuU>1?eu=Wfa;ot@1womCgL4x|*7L;
3381r3@nltxNN9>({DLs>Hp;eNmjYmlhoxs4Lc{TtG1S~dalXk(sNeJ$Cyl$Qb$N5K1(BbWNa(w1Lh-
NZqcbQHp>%XT;yRYV(&W~<a&826Hx3un_Tot%7tmphUThbxt(`@>for