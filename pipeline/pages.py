"""The text pages: about.html, terms.html, privacy.html.

Content lives here as HTML strings; site.py passes in the shared template, nav and footer.
The legal pages are plain-English drafts: have them reviewed before publishing, and fill the
SITE values in site.py (owner, contact email, jurisdiction, host) so no "to be confirmed" markers remain.
"""
import os

def build(ctx):
    S, tbc = ctx["SITE"], ctx["tbc"]
    owner = tbc(S.get("owner"), "site owner")
    email = S["email"] and '<a href="mailto:%s">%s</a>' % (S["email"], S["email"])
    contact = tbc(email, "contact email")
    host = tbc(S["host"], "hosting provider")
    law = tbc(S["jurisdiction"], "governing law")

    ABOUT = ("About", "About this site", "What the chart shows, how to read it, and where the information comes from.", """
<p class="doc__lead">Lineage of the Church sets the leaders of three ancient sees side by side on one timeline: the archbishops of Canterbury,
the bishops of Rome and the patriarchs of Constantinople. Because the lines share the same century rows, you can see at a glance who held
office at the same time, and follow the dotted circles to the families of churches that grew from or alongside them.</p>

<h2>How to read the chart</h2>
<ul>
<li><b>Down the page is forward in time.</b> Each row is a century, and each figure sits in the century in which most of their time in office fell.</li>
<li><b>Selected figures are shown first.</b> Press <b>+ more</b> beside a century to see every holder of the office in that century.</li>
<li><b>Anyone can be opened.</b> Click or tap a person for a short biography, their dates in office and lifespan, and one thing that happened in the wider world while they served.</li>
<li><b>Dashed lines mark the great divisions:</b> 451, after the Council of Chalcedon; 1054, between Rome and Constantinople; and 1534, between England and Rome. The lines carry on through them.</li>
<li><b>Dotted circles open a family of churches:</b> the Oriental Orthodox churches, the wider Orthodox family, the Protestant churches, and the Anglican churches in North America.</li>
</ul>

<h2>What the chart does not claim</h2>
<p>The chart is a timeline, not a verdict. It takes no position on which church is the true continuation of the apostles, or on the
validity of any church&rsquo;s orders. Jesus is named above the three lines as the origin all three claim, not drawn into any one of them.
Rome sits in the centre column only for layout. Each tradition reads the divisions differently: the Orthodox see 1054 as Rome&rsquo;s
departure, Catholics see it the other way, and Anglicans see 1534 as a reform rather than a founding.</p>
<p>The earliest names and dates follow later tradition, and are marked as such where it matters.</p>

<h2>Where the information comes from</h2>
<ul>
<li>Lists of office holders, biographies and portraits come from English Wikipedia and Wikimedia Commons; birth and death years from Wikidata.</li>
<li>The &ldquo;in the world at the time&rdquo; events come from Wikipedia&rsquo;s year articles and a hand-checked timeline. Each event is used once, and falls within that person&rsquo;s time in office.</li>
<li>The information is current as of September 2026. Every biography links to its full Wikipedia article.</li>
</ul>
<p>Biographical text is reproduced from Wikipedia under the <a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="noopener">Creative Commons Attribution-ShareAlike 4.0</a> licence.
Portraits are from Wikimedia Commons, under their individual licences; most are in the public domain.</p>

<h2>Corrections</h2>
<p>Dates in early church history are often disputed, and lists this long contain mistakes. If you spot one, please write to %(contact)s
with the person&rsquo;s name and, if you can, a source.</p>

<h2>Credits</h2>
<p>Site built by %(builder)s. Set in EB Garamond, by Georg Duffner and Octavio Pardo, under the SIL Open Font Licence.</p>
""" % dict(contact=contact, builder=S["builder"]))

    TERMS = ("Terms &amp; conditions", "Terms and conditions", "Last updated %s." % S["updated"], """
<p class="doc__lead">These terms apply to your use of Lineage of the Church (&ldquo;the site&rdquo;), operated by %(owner)s
(&ldquo;we&rdquo;, &ldquo;us&rdquo;). By using the site you agree to them. If you do not agree, please do not use the site.</p>

<h2>1. What the site is</h2>
<p>The site is a free, general-interest reference that sets out the leaders of several churches on a shared timeline. It is for information only.
It is not an official publication of, and is not endorsed by, any church or religious body, and it does not state any church&rsquo;s teaching.</p>

<h2>2. Accuracy</h2>
<p>We work to keep the information accurate, but much of it comes from third-party sources, and early church history is often uncertain or disputed.
The site is provided &ldquo;as is&rdquo;, without any promise that it is complete, accurate or up to date. Please do not rely on it for academic,
legal, genealogical or other decisions without checking a primary source.</p>

<h2>3. Content and licences</h2>
<ul>
<li><b>Wikipedia text.</b> Biographies are reproduced from Wikipedia under <a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="noopener">CC BY-SA 4.0</a>.
You may reuse that text under the same licence, with attribution to Wikipedia.</li>
<li><b>Images.</b> Portraits come from Wikimedia Commons under their own licences, which you must follow if you reuse them.</li>
<li><b>Everything else.</b> The site&rsquo;s design, code, chart layout, illustrations and original writing belong to %(owner)s,
unless stated otherwise. You may link to the site and share screenshots for personal, educational or review purposes with credit.
Please ask us before reproducing it in any other way.</li>
</ul>

<h2>4. Using the site</h2>
<p>Please do not misuse the site: for example, by trying to disrupt it, gain unauthorised access to it, or copy it wholesale by automated means.</p>

<h2>5. Links to other sites</h2>
<p>The site links to Wikipedia and other websites. We do not control them and are not responsible for their content or their privacy practices.</p>

<h2>6. Liability</h2>
<p>To the extent the law allows, we are not liable for any loss arising from your use of the site or your reliance on its content.
Nothing in these terms limits any liability that cannot be limited by law.</p>

<h2>7. Changes</h2>
<p>We may update the site and these terms from time to time. The date at the top shows when the terms last changed.</p>

<h2>8. Governing law</h2>
<p>These terms are governed by the laws of %(law)s.</p>

<h2>9. Contact</h2>
<p>Questions about these terms: %(contact)s.</p>
""" % dict(owner=owner, law=law, contact=contact))

    PRIVACY = ("Privacy policy", "Privacy policy", "Last updated %s." % S["updated"], """
<p class="doc__lead">Lineage of the Church is built to collect as little as possible. There are no accounts, no forms, no advertising,
no analytics and no tracking cookies. This policy explains the little that does happen when you visit.</p>

<h2>Who is responsible</h2>
<p>The site is operated by %(owner)s. You can contact us about privacy at %(contact)s.</p>

<h2>What we collect</h2>
<p>We do not ask for, or store, any personal information about you.</p>

<h2>What is stored on your device</h2>
<p>If you use the light/dark switch, your choice is saved in your browser&rsquo;s local storage under the name <code>theme</code>, so the site remembers it
next time. It never leaves your device, is not a cookie, and is not sent to us. You can clear it at any time through your browser&rsquo;s settings.</p>

<h2>Our hosting provider</h2>
<p>The site is hosted by %(host)s. Like almost every web server, theirs keeps short-lived technical logs of requests (such as IP address,
browser type and the page requested) to deliver the site and keep it secure. We do not use these logs to identify or profile visitors.</p>

<h2>Fonts</h2>
<p>The site&rsquo;s typeface, EB Garamond, is loaded from Google Fonts. When a page loads, your browser requests the font from Google,
which means Google receives your IP address. Google&rsquo;s handling of that information is covered by the
<a href="https://policies.google.com/privacy" rel="noopener">Google Privacy Policy</a>.</p>

<h2>Links to other sites</h2>
<p>Names and events link to Wikipedia and other sites. If you follow a link, that site&rsquo;s own privacy policy applies, such as the
<a href="https://foundation.wikimedia.org/wiki/Policy:Privacy_policy" rel="noopener">Wikimedia Foundation Privacy Policy</a>.</p>

<h2>Children</h2>
<p>The site is suitable for all ages and collects no personal information from anyone, including children.</p>

<h2>Your rights</h2>
<p>Because we hold no personal information about you, there is normally nothing for us to access, correct or delete. If you have a question or
concern, contact us at %(contact)s. You may also have the right to complain to your local data protection authority.</p>

<h2>Changes to this policy</h2>
<p>If the site ever begins to collect information (for example, through analytics or a contact form), we will update this policy first.
The date at the top shows when it last changed.</p>
""" % dict(owner=owner, contact=contact, host=host))

    out = []
    for fname, (short, h1, sub, body) in (("about.html", ABOUT), ("terms.html", TERMS), ("privacy.html", PRIVACY)):
        kicker = "About" if fname == "about.html" else "The small print"
        page = ('%s<div class="page page--doc"><article class="doc" id="chart" tabindex="-1"><header class="doc__head"><span class="mast__kicker">%s</span>'
                '<h1>%s</h1><p class="doc__sub">%s</p></header><div class="doc__body">%s</div></article></div>%s'
                % (ctx["nav"](fname), kicker, h1, sub, body, ctx["footer"]()))
        doc = ctx["TEMPLATE"].format(head=ctx["head"], v_css=ctx["ver"]("assets/css/app.css"), v_js=ctx["ver"]("assets/js/app.js"),
                                     title="%s &middot; %s" % (short, S["name"]), body=page, dialog="")
        doc = doc.encode("ascii", "xmlcharrefreplace").decode("ascii")
        open(os.path.join(ctx["ROOT"], fname), "w", encoding="ascii").write(doc)
        out.append((fname, len(doc)))
    return out
