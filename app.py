from flask import Flask, render_template, request, jsonify, make_response, session, redirect, url_for
from datetime import date
import calendar
import io
import os
from functools import wraps

from numerology import calculate_all, get_personal_month, get_personal_day, get_pinnacles, get_challenges

app = Flask(__name__)
app.secret_key = os.environ.get('ADMIN_PASSWORD', 'dev-secret-fallback')

# ── Supabase ───────────────────────────────────────────────────────────────────
_sb_url = os.environ.get('SUPABASE_URL', '')
_sb_key = os.environ.get('SUPABASE_KEY', '')
db = None
if _sb_url and _sb_key:
    try:
        from supabase import create_client
        db = create_client(_sb_url, _sb_key)
    except Exception:
        pass

# ── Content databases ──────────────────────────────────────────────────────────

MULANK_DATA = {
    1: {"title": "Mulank 1 — Sun", "text": "Born leader, radiates confidence, ambitious, bold, straightforward. Centre of attraction. Freedom lover. Avoid ego and overconfidence.", "favourable": "Mar 21 – Aug 20", "unfavourable": "Oct 15 – Dec 25", "lucky_color": "Red"},
    2: {"title": "Mulank 2 — Moon", "text": "Sensitive, intuitive, emotional, diplomatic. Natural peacemaker. Highly imaginative. Can be indecisive and overly sensitive.", "favourable": "Jul 20 – Aug 20", "unfavourable": "Oct 15 – Nov 14", "lucky_color": "White, Silver, Cream"},
    3: {"title": "Mulank 3 — Jupiter", "text": "Extremely ambitious, self-motivated, social, cheerful, religious. Great communicator and multitasker. Can be bossy.", "favourable": "Mid Feb – Mid Mar and Nov 25 – Dec 25", "unfavourable": "Oct – Nov", "lucky_color": "Yellow, Golden"},
    4: {"title": "Mulank 4 — Rahu", "text": "Practical, hardworking, disciplined, unconventional thinker. Challenges existing norms. Can be stubborn and rigid.", "favourable": "Jun 21 – Aug 20", "unfavourable": "Jan 14 – Feb 14", "lucky_color": "Electric Blue, Grey"},
    5: {"title": "Mulank 5 — Mercury", "text": "Versatile, quick-witted, adaptable, loves freedom and travel. Excellent communicator. Can be restless and inconsistent.", "favourable": "Jun 21 – Aug 20, Sep 21 – Oct 20", "unfavourable": "Dec 25 – Jan 14", "lucky_color": "Green, Light Grey"},
    6: {"title": "Mulank 6 — Venus", "text": "Loving, caring, family-oriented, artistic, harmonious. Natural nurturer. Can be possessive and self-sacrificing.", "favourable": "Apr 20 – May 20", "unfavourable": "Oct 15 – Nov 14", "lucky_color": "Pink, Light Blue, White"},
    7: {"title": "Mulank 7 — Ketu", "text": "Spiritual, introspective, analytical, mysterious. Seeker of truth. Can be isolated and melancholic.", "favourable": "Jul 20 – Sep 20", "unfavourable": "Dec 25 – Jan 14", "lucky_color": "Lavender, Violet"},
    8: {"title": "Mulank 8 — Saturn", "text": "Ambitious, disciplined, powerful, material-minded. Born for power and authority. Can be workaholic and ruthless.", "favourable": "Dec 25 – Jan 14", "unfavourable": "Mar 21 – Apr 20", "lucky_color": "Dark Blue, Black, Brown"},
    9: {"title": "Mulank 9 — Mars", "text": "Courageous, energetic, passionate, humanitarian. Natural warrior. Can be aggressive and impulsive.", "favourable": "Mar 21 – Apr 20", "unfavourable": "Oct 15 – Nov 14", "lucky_color": "Red, Crimson"},
}

MULANK_PDF_DATA = {
    1: "If you are born on the 1, 10, 19, or 28 of any month, your psychic number is 1 and you are ruled by the radiant Sun. Sun makes you a born leader, it makes your presence felt wherever you go and it wont be wrong to say that you are the life of the party. Oozing confidence comes naturally and easily to you. You have high self-esteem and are quite ambitious. You are bold and straightforward, and due to this people sometimes mistake you for being egoistic and arrogant, however, once they get to know you, they realize the warmth you have in your heart for the people around you and your kind spirit. Just like your psychic number, you wanna become number 1 in whatever you do and you also happen to become number 1 as you are stubborn in life, you are ready to burn the midnight oil and put in all your hard work to achieve your goals and dreams even at the cost of inconveniences and sacrifices.\n\nYour triumph and accomplishments are what keep you going and alive. You can take up leadership roles with ease in any sphere of your life and excel at it, be it your social circle, professional life, or personal. You are innovative and have a talent for using language in a charming, effective, and persuasive manner which attracts other people to you and they wish to listen to you. This is the reason why your friends and acquaintances come to you to seek advice. This boosts and motivates you and you also enjoy helping others. It gives you a sense of pride and keeps you propelled. As you are ruled by the Sun which is considered to be the King in Numerology, you desire to live a royal lifestyle and with your efforts and uphill battle, you are also able to achieve it. You love spending money and you spend it extravagantly to attain the luxuries and lavish lifestyle you wish and desire in life. Advice for you would be to keep a check on your savings and finances and not go over budget to achieve materialistic possessions.\n\nYou are always concerned and conscious about your public presence and your image. You enjoy being the centre of attraction just like your ruling planet, the Sun. You are known to carry a charismatic aura and a strong presence which attracts people toward you and creates curiosity in people to get to know you more. People around really enjoy spending time in your company and engaging in conversations with you. You do not like to be dominated or told what to do as you want to live your life and do your things on your terms. In other words, you are a freedom lover and dislike intrusions and interventions in your life and your style of working. You believe in being your own Boss.\n\nSome things that you must keep in mind to avoid discord and disturbances are to not dictate to others or to let your authoritative nature overpower your relationship with others, especially with your family members and friends. You possess a great deal of confidence which is phenomenal but do not let your overconfidence and ego drive your life in the wrong direction and cause distress and disagreements in your life. You indeed find it difficult to change your perception and opinion, but you must try to understand the perspective of others rather than imposing your thought process and ideologies on them. It is also seen that you tend to become discouraged and downhearted when you do not achieve what you desire, you are advised to accept delays and failures as it is all a part of life, a single event cannot decide your fate but a single failure can add a whole lot of experience to your life and put you on the path to success.\n\nFavourable Period: The most favourable time for you is the period between March 21st to August 20th as your birth date ruler, the Sun, is at its strongest and the most active during this season. This time yields prosperous and promising results. You must make optimum use of this period and choose it to start a new venture, make new investments, make new plans and goals, and start an auspicious activity, task, or project.\n\nUnfavourable Period: You must avoid starting any new and important activity from October 15th to December 25th as the Sun is weak during that phase. This term might bring some unwelcoming experiences such as a lack of motivation, procrastination, distractions, delays, stress, health issues, financial losses, unnecessary worries, and false allegations which could lead to defamation.\n\nLucky Colours: Red and shades of red are auspicious for you. You must include them in your daily life and surround yourself with these colours to attract luck. You may wear clothes or accessories associated with that colour, add this colour to your home decor, use red bed sheets, covers, and towels, use a red coloured phone cover, or change your phone lock screen and home screen to red wallpapers.",

    2: "If you are born on the 2nd, 11th, 20th, or 29th of any month, your psychic number is 2 and you are ruled by the gentle Moon. The Moon makes you highly sensitive, intuitive, and emotionally aware. You are a natural peacemaker and diplomat who instinctively understands the feelings of others. Your empathy and compassion draw people to you, and you are often the person others turn to in times of need. You have a rich inner life and a vivid imagination that can be a tremendous creative asset.\n\nYou are naturally cooperative and prefer to work in harmony with others rather than in competition. You thrive in partnerships and collaborations, and your ability to understand multiple perspectives makes you an excellent mediator and counselor. You possess a deep love for beauty, music, and the arts, and you appreciate the finer things in life. Your home is your sanctuary, and you invest great care in creating a warm and welcoming environment for your loved ones.\n\nOne of your greatest gifts is your intuition. You often sense things before they happen, and your gut feelings are remarkably accurate. Learning to trust this inner voice is one of your most important life lessons. However, your sensitivity can also be a vulnerability, as you are easily affected by the emotions and moods of those around you. Developing emotional boundaries will help you maintain your own wellbeing while continuing to support others.\n\nYou can sometimes struggle with indecision, as you are able to see all sides of a situation and find it difficult to commit to one course of action. Learning to make decisions with confidence while honoring your sensitivity is a key growth area for you. You also have a tendency toward self-doubt, and it is important for you to develop self-confidence and trust in your own abilities and judgements.\n\nFavourable Period: The most favourable time for you is between July 20th and August 20th, when the Moon and its energy are most active and supportive. This is an excellent time to begin new ventures, deepen relationships, and pursue creative projects. Make the most of this period for important decisions and new beginnings.\n\nUnfavourable Period: The period between October 15th and November 14th can bring emotional turbulence, indecision, and misunderstandings. Avoid making major decisions during this time and focus instead on introspection and emotional healing.\n\nLucky Colours: White, Silver, and Cream are your most auspicious colours. Wearing or surrounding yourself with these colours can enhance your intuition, bring calm to your emotions, and attract positive energy into your life. Consider using white or silver tones in your home decor, clothing, and accessories.",

    3: "If you are born on the 3rd, 12th, 21st, or 30th of any month, your psychic number is 3 and your ruling planet is Jupiter.\n\nYou are known to be extremely ambitious, by your very own will, and are self-motivated. It wont be wrong to say that hard work gives you pleasure. If you do not work hard, you feel something is missing or as if you are not giving it your 100 per cent. You thrive for bigger things and accomplishments in your professional life and cannot see yourself settling for subordinate positions.\n\nYou want to achieve one thing after the other, and you also make it happen given your devotion, discipline, and commitment to your work. Your dedication is a result of not wanting to see struggles in your life that you might have had to face in your early professional years. Psychic number 3 individuals start their careers early and might have to face hardship during that time which sets them up for success in the future. In reality, it shapes you to face any obstacle and learn how to overcome situations and come out as a winner.\n\nYou learn how to deal with people around you and how to handle situations. You just dont have time to work but also to play. You are social and cheerful and like to engage in conversations with people. You are also known to have a good sense of humour.\n\nYou are religious and have faith in God or the Supreme Power, you may or may not show it to the world but in your heart, you believe in cosmic energy. You like to express yourself with gestures, light humoured jokes and love the attention you get because of it. It would be correct to say you like to be in the spotlight and be the centre of attraction for all good reasons which are, your efforts and your endeavours.\n\nYou are valued for your optimism and for how well you can manage everything. You maintain your personal life equally enjoyable and vivid, however, it is seen that sometimes you find it difficult to draw the line between personal and professional lives which in turn disturbs your work-life balance.\n\nYou can multitask and are great at it. You can perform, manage, and organize several tasks, meetings, responsibilities, and home duties at the same time but your inclination from time to time is more towards your professional life than your personal life.\n\nIn your personal life, you are an extremely caring and loving individual who wants to provide for their family and loved ones. In relationships, you give all you possibly can to make your partner feel loved and secure, however, sometimes your partner will also have to experience your bossy and dictatorial nature.\n\nFavourable Period: The most favourable and beneficial times for you are the periods between Mid February to Mid March and November 25th to December 25th. You must make optimum use of this period to start a new venture, make new investments, create new plans, set your goals, and start an auspicious activity. This period results in being very beneficial for travelling.\n\nUnfavourable Period: You must avoid starting any new and important activities during October and November as they may bring dissatisfactory results. This period is also unfavourable for travelling.\n\nLucky Colours: Yellow, Golden, and shades of yellow and golden are auspicious for you. You must include them in your daily life and surround yourself with these colours to attract luck.",

    4: "If you are born on the 4th, 13th, or 22nd of any month, your psychic number is 4 and you are ruled by the shadow planet Rahu. Rahu makes you unconventional, original, and a challenger of established norms and conventions. You see the world differently from most people and often arrive at solutions and ideas that others overlook. You are practical and hardworking, and once you set your mind to something, you pursue it with tremendous discipline and dedication.\n\nYou possess a powerful intellect and a strong sense of logic. You are methodical in your thinking and prefer to have a solid plan before taking action. Your pragmatic nature means you excel at turning ideas into tangible realities. You are the kind of person who builds things that last, whether in your professional life, your relationships, or your personal projects. People often come to rely on you precisely because of your dependability and your thoroughness.\n\nRahu's influence can create a sense of restlessness and dissatisfaction in you. You may sometimes feel like an outsider or that your unconventional views are not appreciated or understood by those around you. This can lead to feelings of isolation or frustration. However, it is precisely your different perspective that is your greatest gift to the world, and over time, others will come to recognize and value the originality of your thinking.\n\nYou may find that your plans are frequently disrupted or that just when things seem to be going well, an unexpected change of direction occurs. This is a hallmark of Rahu's influence. Learning to embrace change and to adapt your plans without losing sight of your goals is one of the most important lessons for you. Developing focus and learning to direct your energy in a sustained manner will bring you tremendous rewards.\n\nFavourable Period: The period between June 21st and August 20th is your most favourable time. During this period, your efforts are more likely to bear fruit, and new opportunities are more likely to manifest. Take advantage of this window to launch new projects, form important partnerships, and make significant decisions.\n\nUnfavourable Period: The period between January 14th and February 14th may bring challenges, obstacles, and a sense that progress is stalled. Avoid starting new ventures during this time and focus on consolidating existing work and completing ongoing projects.\n\nLucky Colours: Electric Blue and Grey are your most auspicious colours. Incorporating these shades into your wardrobe, accessories, and living space can help you harness Rahu's positive energy while grounding your unconventional ideas in practical reality.",

    5: "If you are born on the 5th, 14th, or 23rd of any month, your psychic number is 5 and you are ruled by the planet Mercury. Mercury bestows upon you a quick mind, excellent communication skills, and an insatiable curiosity about the world around you. You are versatile, adaptable, and thrive on variety and stimulation. You are the kind of person who can effortlessly move between different social circles, topics, and activities, and you rarely stay in one place or one state of mind for long.\n\nYou possess a natural gift for communication in all its forms, whether it is writing, speaking, negotiating, or simply engaging in conversation. People enjoy your company because you bring energy, wit, and fresh perspectives to every interaction. You are quick-witted and have a wonderful sense of humor that can lighten any situation. Your ability to think on your feet and adapt to changing circumstances is one of your most valuable assets in both your personal and professional life.\n\nYou have a deep love of freedom and independence and resist anything that feels confining or restrictive. Travel, new experiences, and learning are among your greatest joys. You are drawn to people and ideas that are different from what you already know, and you are constantly adding to your storehouse of knowledge and experience. This adventurous spirit keeps you young at heart and ensures that life rarely becomes dull or routine.\n\nOne of the challenges you may face is a tendency toward restlessness and inconsistency. You may find it difficult to stick with one thing long enough to master it fully, or you may start many projects without completing them. Developing discipline and the ability to focus your considerable energy will be one of your most important growth areas. Learning to channel your natural versatility into sustained effort will allow you to achieve truly remarkable results.\n\nFavourable Period: Your most favourable periods are June 21st to August 20th and September 21st to October 20th. During these times, Mercury's influence is strongest and most supportive, making them ideal for communication, negotiations, travel, learning, and launching new ventures.\n\nUnfavourable Period: The period between December 25th and January 14th may bring miscommunications, travel delays, and a scattering of energy. Avoid signing important contracts or making major commitments during this time, and focus on review and reflection rather than new initiatives.\n\nLucky Colours: Green and Light Grey are your most auspicious colours. Green, in particular, resonates with Mercury's energy and can help sharpen your intellect, improve your communication, and attract good fortune. Include these colours in your daily life through clothing, accessories, and your living environment.",

    6: "If you are born on the 6th, 15th, or 24th of any month, your psychic number is 6 and you are ruled by the beautiful planet Venus. Venus blesses you with a deep love of beauty, harmony, and the finer things in life. You are naturally charming, warm, and magnetic, and people are drawn to your gentle yet radiant presence. You have a strong aesthetic sense and a talent for creating beautiful environments and experiences for those around you.\n\nYou are a natural nurturer and caregiver, and your family and loved ones are of paramount importance to you. You invest deeply in your relationships and give freely of your time, energy, and love. Your home is your pride and joy, and you work hard to make it a haven of comfort and beauty. You have a strong sense of responsibility and take your duties to others seriously, sometimes to the point of placing their needs ahead of your own.\n\nYou possess artistic talents and an appreciation for music, art, and culture. Whether or not you pursue a formal creative career, bringing beauty into the world in some form is a deep calling for you. You have an eye for aesthetics and a gift for harmony, and these qualities enrich every area of your life. People often turn to you for advice on matters of taste, relationships, and how to create more beauty and balance in their own lives.\n\nOne of the challenges for you is a tendency toward possessiveness and a difficulty letting go, whether in relationships, situations, or material things. Learning to love with an open hand and to trust that what is truly yours will remain with you is one of your most important life lessons. You may also have a tendency toward self-sacrifice that can lead to resentment over time. Developing healthy boundaries and learning to receive as graciously as you give will bring greater balance and fulfillment.\n\nFavourable Period: Your most favourable period is April 20th to May 20th, when Venus's energy is at its most potent. This is an ideal time for romantic matters, creative projects, financial decisions, and anything to do with beauty, art, or relationships. Make the most of this window for important new beginnings.\n\nUnfavourable Period: October 15th to November 14th can bring challenges in relationships, financial matters, and creative endeavors. Focus on maintaining existing commitments during this period rather than initiating new ones.\n\nLucky Colours: Pink, Light Blue, and White are your most auspicious colours. These shades resonate beautifully with Venus's energy and can help attract love, creativity, and harmony into your life. Wear them, decorate with them, and surround yourself with them as often as possible.",

    7: "If you are born on the 7th, 16th, or 25th of any month, your psychic number is 7 and you are ruled by the mystical shadow planet Ketu. Ketu bestows upon you a deep spiritual nature, a powerful intuition, and a profound wisdom that often sets you apart from those around you. You are a natural seeker of truth and meaning, and you are rarely satisfied with surface-level explanations or shallow experiences. You have a penetrating mind that delves beneath appearances to find deeper truths.\n\nYou are highly introspective and need regular periods of solitude and quiet reflection to process your experiences and reconnect with your inner wisdom. You are deeply philosophical by nature and are drawn to the great questions of life, spirituality, and existence. Many people with psychic number 7 find themselves drawn to meditation, philosophy, metaphysical studies, or other practices that help them explore the deeper dimensions of reality.\n\nYou possess excellent analytical and research abilities and can focus on a subject with remarkable concentration and depth. You are thorough and methodical in your thinking and tend to arrive at highly original insights and conclusions. Your mind works best when it is given time to go deep rather than wide, and your best work often comes from sustained periods of focused study and reflection. You may seem quiet or reserved to others, but beneath this exterior lies a rich inner world that is constantly alive with insight and intuition.\n\nYour challenge is to share your gifts and insights with others rather than keeping them to yourself. There can be a tendency toward isolation or a preference for the inner world over the outer one, and developing the ability to communicate your wisdom to others is one of your most important growth areas. You may also at times feel melancholy or struggle with feelings of being misunderstood. Learning to connect with others who share your depth and to find communities that value your kind of intelligence will bring you much greater joy.\n\nFavourable Period: Your most favourable period is July 20th to September 20th, when Ketu's energy is most supportive of your deeper nature. This is an excellent time for spiritual practices, research, study, and any projects requiring deep thought and analysis. Important insights and breakthroughs are more likely to occur during this period.\n\nUnfavourable Period: December 25th to January 14th may bring a sense of confusion, withdrawal, or lack of direction. Avoid major decisions during this time and focus on inner work, meditation, and self-care.\n\nLucky Colours: Lavender and Violet are your most auspicious colours. These spiritual shades resonate with Ketu's otherworldly energy and can help deepen your intuition, enhance your spiritual awareness, and bring clarity to your thoughts. Use them in your clothing, accessories, and living environment.",

    8: "If you are born on the 8th, 17th, or 26th of any month, your psychic number is 8 and you are ruled by the powerful planet Saturn. Saturn is the planet of karma, discipline, and hard work, and its influence makes you one of the most ambitious, determined, and capable individuals in all of numerology. You are built for success and for positions of authority and power. You understand intuitively that great achievements require great effort, and you are willing to pay the price.\n\nYou possess exceptional organizational abilities, a strong sense of discipline, and an executive mind that is capable of managing complex systems, projects, and people. You have a natural authority and gravitas that others respect, and you often find yourself in positions of leadership and responsibility, whether you sought them out or not. You are not afraid of hard work or of the challenges and obstacles that life puts in your path. In fact, you often perform best when faced with adversity, which has the effect of sharpening your focus and bringing out your formidable reserves of determination.\n\nSaturn's influence also gives you a deep connection to karmic principles. You understand that actions have consequences and that what you put out into the world will return to you. This wisdom, when fully internalized, makes you a person of great integrity and ethical strength. You are also deeply concerned with building something lasting and substantial, whether in your career, your financial life, or your contribution to society. Legacy matters deeply to you.\n\nOne of the significant challenges for those with psychic number 8 is the tendency to become so absorbed in work and material achievement that personal relationships and health are neglected. Saturn can also bring a certain heaviness or seriousness to your personality that can make it difficult to relax and enjoy the lighter aspects of life. Learning to balance your tremendous drive for achievement with joy, play, and nurturing connection with others is one of the most important lessons for you.\n\nFavourable Period: Your most favourable period is December 25th to January 14th, when Saturn's energy is at its peak. This is an excellent time to make important career decisions, launch business ventures, set long-term financial goals, and consolidate your position and resources.\n\nUnfavourable Period: March 21st to April 20th may bring obstacles, conflicts with authority, or setbacks in your plans. It is wise to avoid major confrontations or bold new initiatives during this period and to focus instead on patient, steady progress.\n\nLucky Colours: Dark Blue, Black, and Brown are your most auspicious colours. These earthy, powerful shades resonate with Saturn's energy and can help you project authority, attract material success, and maintain focus on your long-term goals.",

    9: "If you are born on the 9th, 18th, or 27th of any month, your psychic number is 9 and you are ruled by the dynamic and energetic planet Mars. Mars bestows upon you tremendous courage, energy, passion, and drive. You are a natural warrior and fighter who approaches life with boldness and intensity. You are not the kind of person who sits on the sidelines while life passes by. You engage with the world fully and directly, bringing your considerable fire and determination to everything you do.\n\nYou have a deep humanitarian streak and a genuine concern for the wellbeing of others. You are often drawn to causes, movements, or professions where you can make a positive difference in the world and stand up for those who cannot stand up for themselves. Your passion and conviction are inspiring to others, and you have a natural ability to mobilize people and lead them toward a common goal. Whether in your professional life or your personal relationships, you bring tremendous energy, loyalty, and generosity to everything you commit to.\n\nYou possess natural leadership qualities and a directness of expression that people often find refreshing, though it can sometimes come across as blunt or even aggressive. You speak your mind without hesitation and have little patience for dishonesty, manipulation, or timewasting. Your standards are high, both for yourself and for those around you, and you can become frustrated or impatient when others do not match your level of commitment and effort. Learning to channel your intensity in constructive directions is one of your most important ongoing practices.\n\nOne of the challenges for psychic number 9 individuals is a tendency toward impulsiveness and a difficulty controlling anger when provoked. Mars's fiery energy needs healthy outlets, such as physical exercise, sports, or creative expression, to prevent it from turning into frustration or conflict. Developing patience and the ability to see situations from multiple perspectives will serve you enormously in your relationships and your career.\n\nFavourable Period: March 21st to April 20th is your most favourable period, when Mars's energy is at its most powerful and supportive. This is an excellent time to launch new ventures, take on challenging projects, assert yourself in important situations, and pursue your most ambitious goals.\n\nUnfavourable Period: October 15th to November 14th can bring conflict, frustration, and depletion of energy. Avoid confrontations and impulsive decisions during this period, and focus on conserving your energy and working steadily rather than forcing outcomes.\n\nLucky Colours: Red and Crimson are your most auspicious colours. These powerful, energetic shades resonate with Mars's fiery nature and can help amplify your confidence, courage, and natural leadership qualities. Wear them, use them in your home decor, and surround yourself with these colours to attract Mars's positive energy.",
}

BHAGYANK_DATA = {
    1: "Destiny of leadership and individuality. Blessed with originality and pioneering spirit. Must develop independence and avoid dependence on others. Success through self-effort.",
    2: "Destiny of harmony and cooperation. Natural diplomat and mediator. Success through partnerships and teamwork. Must avoid over-sensitivity and indecision.",
    3: "Destiny of creativity and self-expression. Blessed with communication skills and optimism. Success through creative pursuits and social connections. Avoid scattering energy.",
    4: "Mental power, practicality, reads between the lines. Plans often get disrupted. Fickle focus due to Rahu influence. Unconventional ideas that take time to be accepted. Rely on brain over brawn. Maintain focus for miracles.",
    5: "Destiny of freedom and change. Highly adaptable, loves travel and variety. Success through versatility and communication. Must develop discipline and consistency.",
    6: "Destiny of love and responsibility. Natural caretaker and harmonizer. Success through service to family and community. Must avoid martyrdom and possessiveness.",
    7: "Spirituality and intuition. Becomes everyone's favourite naturally. Healer by nature - talking to them comforts others. Wisdom and deep knowledge. Foreign recognition likely. If married before 28, marital issues possible. Drawn to occult sciences later in life.",
    8: "Destiny of power and material achievement. Must overcome obstacles to reach success. Karmic lessons around money and authority. Great potential for business and leadership.",
    9: "Destiny of humanitarian service. Strong idealism and compassion. Success through helping others and fighting for causes. Must channel aggression productively.",
}

BHAGYANK_PDF_DATA = {
    1: "It is ruled by the Sun.\n\nDestiny number 1 represents leadership, independence, and the pioneering spirit. You are destined to stand out, to lead, and to carve new paths that others will follow. The Sun's influence on your destiny number ensures that leadership and authority are natural themes throughout your life. From an early age, you likely found yourself taking charge of situations, whether formally or informally, and others naturally looked to you for direction and guidance.\n\nYou possess strong willpower, determination, and an innate drive to achieve and excel. You have original ideas and the confidence to pursue them even when others are skeptical. Your destiny is to develop your own unique identity and to follow your own path rather than conforming to the expectations of others. You do your best work when you have the freedom to operate independently and to make your own decisions.\n\nThe path of DN 1 brings you opportunities to lead in multiple spheres of your life, but it also brings the lesson of learning to balance leadership with humility. The greatest leaders know how to inspire and empower those around them rather than simply dominating. Learning to listen, to collaborate, and to acknowledge the contributions of others will be one of your most important ongoing growth areas.\n\nDN 1 individuals often experience significant new beginnings in their lives, whether in the form of new careers, relocations, relationships, or personal transformations. These new beginnings are often catalyzed by your own courage and initiative. You are the kind of person who makes things happen rather than waiting for life to happen to you, and this proactive quality is one of your greatest strengths.",

    2: "It is ruled by the Moon.\n\nDestiny number 2 represents cooperation, harmony, and the deep power of relationships. You are destined to be a bridge-builder, a mediator, and a creator of harmony in whatever sphere of life you inhabit. The Moon's influence on your destiny number gives you exceptional sensitivity to the emotional currents around you and a natural gift for understanding and supporting others. Your life path brings you into the realm of relationships, partnerships, and collaborative endeavors.\n\nYou have a powerful intuition that grows stronger as you age, and learning to trust and honor this inner knowing is one of your most important life lessons. The Moon's influence can make you highly sensitive to your environment, to other people's moods, and to subtle energies that others may not even notice. This sensitivity is both your greatest gift and one of your greatest challenges. It enables you to connect deeply with others, but it can also leave you feeling overwhelmed or drained if you do not develop healthy boundaries.\n\nDN 2 brings opportunities for deep and meaningful partnerships throughout your life, both professional and personal. Your greatest successes are likely to come through collaboration and cooperation rather than solo effort. You excel at supporting and enhancing the work of others, at finding common ground between opposing viewpoints, and at creating environments of trust and mutual understanding. Diplomacy and tact are among your most valuable tools.\n\nOne of the key lessons of DN 2 is learning to value your own needs and to assert yourself without losing your natural gentleness and consideration for others. You may have a tendency to put others first to such an extent that your own needs go unmet. Developing the confidence to advocate for yourself while maintaining your gracious and harmonious nature is one of the most important aspects of your destiny.",

    3: "It is ruled by Jupiter.\n\nDestiny number 3 represents creativity, self-expression, and the power of joyful communication. You are destined to share your gifts with the world through your words, your art, your ideas, and your irrepressible sense of joy and optimism. Jupiter's expansive and generous influence on your destiny number ensures that creativity and self-expression are central themes throughout your life. You are meant to inspire, uplift, and delight those around you.\n\nYou are blessed with a natural gift for communication and a charisma that draws others to you. Whether through writing, speaking, performing, or simply engaging in conversation, you have the ability to captivate and inspire your audience. You are naturally optimistic and have an infectious enthusiasm that lifts the spirits of those around you. People feel better for having spent time in your company, and this is one of the most precious gifts you bring to the world.\n\nJupiter's influence also brings a love of learning, travel, and philosophical exploration to your destiny. You are drawn to big ideas and to experiences that expand your understanding of life and the world. You have a natural generosity of spirit and enjoy sharing what you know and what you have with others. Teaching, mentoring, and guiding others may be important aspects of your life path, whether formally or informally.\n\nOne of the key challenges of DN 3 is learning to channel your expansive creative energy in a focused and disciplined way. You have so many ideas and interests that it can be difficult to commit fully to any one path. Developing the discipline to follow through on your creative projects and commitments will enable you to fully realize your considerable potential. The world needs what you have to offer, and it is worth the effort of bringing your gifts to full expression.",

    4: "It is ruled by the shadow planet Rahu.\n\nDestiny number 4 represents mental power, intellectual prowess, and practicality. You are clever and adept at reading between the lines. You highly likely comprehend the original motives and intentions of others by merely having a conversation with them. Its rather unfortunate that people often misunderstand you. You try to convey one thing, but they interpret it wrongly. This misunderstanding makes it utterly difficult to be in their good graces. This is the chief reason why you may find yourself ending up with only a handful of friends after a certain age, or find it hard to make friends. You are careful, proactive, and like to plan things ahead of time. You are practical and your pragmatic approach brings favorable results.\n\nRahu is a mischievous and dynamic planet that never likes to stay in one place. It shows its influence on various aspects of your life:\n- You would find yourself making big career plans for the future, but end up doing something entirely different.\n- You would feel something is always missing in life, you cannot put your finger on it, even when you have everything you need.\n- Rahu brings disappointment in at least one facet of your life.\n- Health issues become a concern as well.\n- Although you have the stamina to tackle physical work, your physical labour gets unnoticed. Rahu makes it almost certain that the output of brain activity is far superior and appreciated than the result of any physical activity.\n- As Rahu doesnt stay put, it affects your focus. You would find yourself most productive when focused, but your focus flutters frequently.\n- Rahu is known to be highly fickle and destroys masterplans. If you notice impedance and disruption in your plans, this is the reason.\n- You may miss out on opportunities because of your sceptical nature.\n- Unavoidable additional responsibilities and duties are likely to come your way.\n\nIn numerology, the number 4 also represents unconventional ways, revolutions, and challenging existing notions. The best way to get the most out of your destiny is:\n- The more you rely and utilize your brain over brawn, the faster you accomplish your goals.\n- Resort to criticism and bluntness only when required.\n- Maintain focus and do activities that enforce your focus. The results will be nothing short of a miracle.",

    5: "It is ruled by Mercury.\n\nDestiny number 5 represents freedom, versatility, and the transformative power of change and experience. You are destined to be an agent of change in your own life and in the lives of those around you. Mercury's quicksilver influence on your destiny number ensures that adaptability, communication, and the embrace of variety are central themes throughout your life journey. You thrive on movement, on new experiences, and on the stimulation of the unexpected.\n\nYou are destined to experience many different phases, environments, and roles throughout your life, and each of these experiences contributes to the richness and depth of your character. Your destiny is not one of sameness or routine but of constant evolution and discovery. This can be both exhilarating and challenging, as it requires you to remain flexible and open to change even when stability and predictability feel more comfortable.\n\nDN 5 brings opportunities for travel, learning, and the exploration of diverse cultures, ideas, and ways of life. Your best opportunities often come through unexpected channels, through chance meetings, sudden opportunities, or changes of direction that you did not plan. Learning to remain alert to these unexpected openings and to have the courage to seize them when they appear is one of the most important skills for you to develop.\n\nOne of the key lessons of DN 5 is learning to develop discipline and follow-through amid all the variety and change that defines your path. There can be a tendency to move on before things are fully completed, or to shy away from commitments that feel too restrictive. Finding the balance between your need for freedom and the stability and depth that come from genuine commitment will be one of the most rewarding aspects of your journey.",

    6: "It is ruled by Venus.\n\nDestiny number 6 represents love, responsibility, and the sacred calling of service to family and community. You are destined to be a nurturer, a harmonizer, and a creator of beauty in the world. Venus's gracious and loving influence on your destiny number ensures that relationships, beauty, and a deep sense of responsibility are central themes throughout your life. Your destiny is to give love freely and to create environments of harmony and care wherever you go.\n\nYou are destined to take on significant responsibilities in your life, often in the role of caregiver, provider, or protector. Whether through your family, your profession, or your community, you will find yourself called to serve and to support others. This is not a burden but a calling that, when embraced fully, brings you deep satisfaction and a profound sense of purpose. You are at your best when you are contributing to the wellbeing of others and when your environment reflects the beauty and harmony you carry within you.\n\nVenus's influence also makes you deeply attuned to aesthetics, art, and the beauty of the natural world. You may have significant artistic talent, or you may simply have a highly developed sense of beauty that expresses itself in the way you dress, decorate your home, or curate the experiences you share with others. Creating beauty is one of the ways you give love to the world, and this is a gift that should not be underestimated.\n\nOne of the key lessons of DN 6 is learning to set healthy boundaries and to avoid the trap of martyrdom. Your deep desire to give and to serve can sometimes lead you to give more than you have, leaving you depleted and resentful. Learning to receive as graciously as you give and to nurture yourself with the same love and care you offer to others will enable you to sustain your gifts and to serve from a place of genuine fullness rather than depletion.",

    7: "It is ruled by half-planet Ketu.\n\nDestiny number 7 represents spirituality and intuition.\n\nThe greatest attribute of DN 7 is its power to enhance the qualities of your Psychic Number manyfold. You would notice that you possess superior qualities of your Psychic Number than you would find in others with the same Psychic Number.\n\nDN 7 blesses you with the power of adaptability, hence you will find yourself easily adjusting to changing times and situations. You would find it natural to keep yourself in touch with the changing technologies and ideas and bring about these changes in yourself to remain abreast of the ever-changing world.\n\nYou are prompt in distinguishing a good trait in a person and accepting and blending it with your traits naturally. You would find that you end up becoming everyones favourite. It is due to DN 7 that enables you to organically understand others and their emotions.\n\nDN 7 highlights intuition. You would realize that as you enter your late twenties, you become highly intuitive and it lasts till you are well in your forties. You may develop a superior instinct for reading people. You would realize that you become very perceptive and understand people without them giving you much information.\n\nYou get your best ideas in your dreams and while daydreaming. Unlike others, who may be quick to reject such ideas, you take them constructively and are prompt to act on them.\n\nDestiny Number 7 also makes you a healer. By merely talking to you, others feel comforted. They seek out your company when they are distressed, dismayed, or dejected. You may not like the person or vice versa, but your advice is always for the betterment of that individual. With this healing power, you may pick out a career in the line of mental and physical healing.\n\nAs ruled by Destiny Number 7, you would find that you get confused easily. When in confusion, the first instinct could be to run away from the problem instead of tackling it. On the other hand, when pushed and encouraged by another person, you power through the situation.\n\n7 is also the number that denotes wisdom. It is right to say that you are a knowledgeable person and demonstrate your knowledge fluently and proficiently, making you a good orator and a brilliant narrator.\n\nDestiny Number 7 brings recognition in foreign countries. You may be showered with plenty of opportunities to work abroad and make a name for yourself.\n\nAs ruled by Destiny Number 7, marital and romantic relationship problems sometimes become inevitable. It has been seen that if people get married after 28, they are more likely to enjoy a successful marriage.\n\nIt is likely for you to develop a strong inclination toward spirituality and occult sciences at a later age. You would find it rather fascinating and end up doing exceedingly well if it is chosen as a career field.",

    8: "It is ruled by Saturn.\n\nDestiny number 8 represents power, material mastery, and the fulfillment of ambitious goals through sustained effort and integrity. You are destined to achieve significant material success and to exercise authority and influence in your professional sphere. Saturn's demanding and karmic influence on your destiny number ensures that themes of hard work, discipline, and the responsible use of power are central to your life journey. Your path is one of building, achieving, and leaving a lasting legacy.\n\nDN 8 is often associated with financial success and business acumen, but it also carries significant karmic weight. Saturn, the planet of karma, ensures that your rewards are directly proportional to your efforts and the integrity with which you operate. You cannot cut corners on the path of DN 8. The universe will hold you accountable, and shortcuts taken will inevitably lead to setbacks. However, when you operate with discipline, honesty, and sustained effort, the rewards can be extraordinary.\n\nYou are destined to develop executive capabilities and to demonstrate that you can handle significant responsibility. This may manifest through corporate leadership, entrepreneurship, financial management, or any other field where strategic thinking and the ability to manage resources and people are paramount. You have the potential to build something truly lasting, something that makes a difference not just in your own life but in the lives of many others.\n\nOne of the key challenges of DN 8 is maintaining balance between your material ambitions and your personal and spiritual life. Saturn's relentless drive for achievement can lead to workaholism and the neglect of relationships, health, and inner development. Learning to honor all dimensions of your life and to recognize that true success encompasses wellbeing, love, and wisdom, not just material achievement, will be one of the most transformative lessons of your journey.",

    9: "It is ruled by Mars.\n\nDestiny number 9 represents completion, universal compassion, and the fulfillment of your purpose through service to humanity. You are destined to be an inspiration to others, to champion important causes, and to leave the world a better place than you found it. Mars's passionate and courageous influence on your destiny number ensures that idealism, compassion, and a burning desire to make a difference are central themes throughout your life. You are meant to live for something larger than yourself.\n\nDN 9 is the number of the humanitarian, and you will find throughout your life that your most meaningful experiences and greatest fulfillments come through giving, serving, and contributing to the wellbeing of others. You have a broad and inclusive perspective that allows you to see beyond personal, cultural, or national boundaries, and you feel a genuine kinship with all of humanity. This expansive compassion is one of your most precious gifts and one of the cornerstones of your destiny.\n\nYour path is also one of completion and release. DN 9 carries within it the energy of all the numbers that precede it, and part of your destiny is to integrate the lessons of all those experiences and to release what no longer serves your highest growth. You may find that you go through several distinct phases or chapters in your life, each one requiring you to let go of what has been accomplished and to open yourself to a new cycle of experience and growth.\n\nOne of the key lessons of DN 9 is learning to channel your idealism and passion in practical directions. There can be a tendency to scatter your energy across too many causes or to burn yourself out in the service of others. Learning to focus your tremendous compassion and drive, to complete what you begin, and to honor your own needs as well as those of others will enable you to sustain your service and to realize the full power of your extraordinary destiny.",
}

LOVE_SEX_PDF_DATA = {
    1: "As a Destiny Number 1, you approach love and intimacy with the same boldness and directness that you bring to all aspects of life. You are passionate, determined, and fully invested when you choose to commit to a partner. You need a relationship where you can maintain your independence while also feeling deeply connected. A partner who admires your strength and supports your ambitions will bring out the very best in you.\n\nYou tend to take the lead in romantic relationships and prefer a partner who appreciates your initiatives. You are generous and warm with those you love, though you may sometimes prioritize your own desires and goals above your partner's needs. Learning to truly listen and respond to your partner's emotional world will deepen your connections significantly.\n\nIn the bedroom, your passion and confidence make you an attentive and energetic partner. You enjoy being in control and creating memorable experiences. The key to lasting fulfilment is learning to balance your natural dominance with a genuine openness to your partner's desires and needs.",

    2: "With Destiny Number 2, your love life is characterized by deep emotion, tenderness, and a profound desire for closeness and security. You are one of the most romantic and devoted partners in the numerology spectrum. You love deeply and give fully in relationships, creating an atmosphere of warmth, intimacy, and genuine emotional connection. For you, love is not just a feeling but a sacred bond.\n\nYou are highly attuned to your partner's moods and needs, often sensing what they feel before they express it. This sensitivity is your greatest romantic gift, but it can also make you vulnerable to hurt and disappointment. You may find yourself giving far more than you receive and need to ensure that your emotional needs are also being met in your relationships.\n\nIntimacy with a Destiny Number 2 individual is tender, sensual, and deeply meaningful. You prefer slow, romantic encounters filled with emotional presence over purely physical experiences. Touch, closeness, and genuine emotional connection are what fuel your deepest satisfaction in love.",

    3: "Destiny Number 3 brings a joyful, playful, and creatively expressive quality to your love life. You are charming, romantic, and naturally magnetic, drawing partners to you with your wit, warmth, and infectious enthusiasm. You approach relationships with an open heart and a spirit of adventure, always looking for ways to keep the spark alive and the connection vibrant. Love, for you, is one of life's greatest sources of joy and inspiration.\n\nYou are a natural flirt and enjoy the art of courtship and romance. You express your love through words, gestures, and creative acts, and you appreciate partners who can match your expressiveness and keep up with your lively spirit. Boredom is your greatest romantic adversary, and you need variety, humor, and genuine mental stimulation to keep you engaged and committed.\n\nIn intimate moments, you bring creativity, playfulness, and genuine warmth. You thrive when your partner appreciates your efforts at romance and reciprocates with their own expressions of affection. The key to lasting love for you is finding someone who can engage your mind as well as your heart.",

    4: "Navigating emotions, especially understanding your partner's passions, may pose challenges for you. Your approach to lovemaking is deliberate, preferring a slow and steady buildup of intensity.\n\nRelationships hold great significance for you, and your loyalty is unwavering. However, overthinking the task of making your partner happy can make lovemaking feel more like a duty than an expression of passion. To avoid stagnation, balance your intellectual approach with a willingness to explore new methods of arousal.\n\nIn your optimal state with a 4 Destiny Number, you embody solidity, loyalty, and accessibility. Tactile yet practical techniques characterize your approach in the bedroom, as you value a certain level of sexual engagement for balance.\n\nAs a no-nonsense lover, you excel in mastering techniques and may benefit from a partner with a more experimental spirit to introduce variety. Alternatively, you find fulfilment in a predictable yet satisfying sexual routine.\n\nObstacles may arise from an aversion to settling down, manifesting as bed-hopping and fear of emotional connection. To avoid a sexual rut, consider alternating between slow, gentle encounters and occasional wild experiences, or even trying outdoor lovemaking. For ladies, embracing the color green can amplify your sensual side.",

    5: "With Destiny Number 5, your approach to love and intimacy is characterized by a love of freedom, variety, and the thrill of discovery. You are adventurous and spontaneous in relationships, always seeking new ways to explore and deepen your connection with your partner. You resist routine and thrive when your relationship feels fresh, exciting, and full of possibility. You need a partner who can embrace your free spirit rather than trying to contain it.\n\nYou are naturally charming and attractive, and you typically have no shortage of romantic interest. Your challenge is finding a partner who can hold your attention for the long term. Once you do find someone who stimulates your mind and matches your zest for life, you are capable of deep and genuine commitment. The key is ensuring that the relationship continues to grow and evolve rather than stagnating.\n\nIn intimate moments, you bring energy, creativity, and a sense of fun. You enjoy variety and experimentation, and you are most fulfilled with a partner who is open-minded and adventurous. Keeping the physical and emotional dimensions of your relationship fresh and unpredictable is the secret to your long-term happiness in love.",

    6: "Destiny Number 6 makes you one of the most devoted, nurturing, and romantically generous partners in all of numerology. You love deeply and completely, investing your heart, time, and energy fully into the relationships that matter to you. Creating a loving, harmonious, and beautiful environment for your partner and family is one of your greatest sources of joy and fulfilment. Love, for you, is an act of service and a calling.\n\nYou are deeply sensual and appreciate the beauty and tenderness that intimacy can bring. You are attentive to your partner's needs and derive great pleasure from making them feel cherished and cared for. However, your deep desire to give and to please can sometimes tip into self-sacrifice, and it is important for you to also receive love and appreciation in return. A relationship where you feel truly valued will bring out your most radiant and generous self.\n\nIn intimate moments, you are warm, sensual, and deeply present. You prefer romantic and emotionally connected encounters over purely physical ones, and you thrive when love is expressed in all the small everyday gestures of care and devotion. Learning to openly express your own needs and desires as well as attending to your partner's is the key to your deepest fulfilment in love.",

    7: "You possess a dreamy and romantic nature, harboring a secret desire for a spiritual connection with your lover. Intellect holds great importance for you, emphasising the need to trust both your partner and yourself. Overanalyzing situations may cause you to miss out on profound connections, so it's essential to relax and let go occasionally. In your optimal state with a 7 Destiny Number, you embody mystery, analytical prowess, and deep thinking.",

    8: "With Destiny Number 8, your approach to love is shaped by the same qualities that define your professional life — intensity, loyalty, high standards, and a deep desire for genuine partnership. You take relationships seriously and are not interested in superficial connections. When you commit to someone, you do so with your full self and expect the same level of dedication and respect in return. A relationship, for you, is a partnership of equals built on mutual respect and shared goals.\n\nYou may not always be the most demonstrative or emotionally expressive partner, but your depth of feeling runs very deep. You show love through acts of provision, loyalty, and protection rather than through words or grand romantic gestures. Your partner will always know they can rely on you, and your steadfast commitment is one of your most profound gifts in a relationship.\n\nIn intimate moments, your intensity and passion are formidable. You bring the same focus and power to your love life as you do to your professional pursuits. The key for you is learning to be vulnerable and to allow your partner to see beyond your formidable exterior to the passionate, deeply feeling person within. Relationships that allow for both strength and vulnerability are the ones that will bring you the deepest satisfaction.",

    9: "Destiny Number 9 brings a passionate, idealistic, and deeply generous quality to your love life. You love with great intensity and give freely of yourself in relationships, often putting your partner's needs and happiness above your own. You have high ideals when it comes to love and are drawn to deep, meaningful connections that feel purposeful and transcendent. For you, a great love is one of the most precious experiences life can offer.\n\nYou are fiercely loyal once you have given your heart and can love with a depth that few can match. However, your tendency to idealize your partner may lead to disappointment when reality falls short of your romantic vision. Learning to love the real person in front of you, with all their human imperfections, is one of your most important lessons in love.\n\nIn intimate moments, you bring passion, generosity, and a desire for deep connection. You thrive when your relationship has both emotional depth and physical intensity, and you are most fulfilled when love is experienced as a profound meeting of souls. Taking time to communicate openly with your partner about your deepest needs and desires will help you build the truly extraordinary love that you deserve.",
}

LOVE_SEX_DATA = {
    1: "Passionate and dominant lover. Strong physical attraction. Independent in relationships - needs space. Can be self-centered. Best with partners who admire their strength.",
    2: "Romantic, tender, and deeply emotional. Craves intimacy and closeness. Highly sensitive to partner's needs. Can become too dependent. Needs reassurance.",
    3: "Playful, flirtatious, and creative in love. Needs mental stimulation and fun. Can be inconsistent in emotions. Keeps relationships lively with humor and spontaneity.",
    4: "Deliberate, slow and steady buildup of intensity. Loyalty is unwavering. Overthinking can make lovemaking feel like a duty. Balance intellectual approach with willingness to explore. Practical yet deeply committed.",
    5: "Adventurous and experimental lover. Needs variety and excitement. Can be commitment-phobic. Charming and irresistible. Best with open-minded partners.",
    6: "Deeply romantic, sensual, and devoted. Creates beautiful experiences for partner. Gives everything in love. Can be overly possessive. Needs to feel cherished and valued.",
    7: "Dreamy and romantic, harbors secret desire for spiritual connection. Intellect holds great importance. Trust is essential. Avoid overanalyzing or you miss profound connections. Mystery and deep thinking characterize your style.",
    8: "Intense and powerful lover. Views relationships as partnerships of equals. Can be controlling. Needs loyalty and respect. Deeply passionate beneath the serious exterior.",
    9: "Passionate, generous, and idealistic in love. Can fall hard and fast. Prone to putting partners on pedestals. Needs to avoid being too self-sacrificing. Deeply loyal once committed.",
}

CONNECTION_DATA = {
    1: "Step into your leadership role with confidence. Trust your instincts and pioneering ideas. Develop your independence and unique identity. Avoid imitating others - your originality is your greatest strength.",
    2: "Nurture your relationships with care and sensitivity. Develop your intuition and trust your inner voice. Practice diplomacy in all interactions. Your gift for harmony can create beautiful partnerships.",
    3: "Cultivate creativity through dancing, acting, poetry, or writing. Nurture self-confidence and embrace a more relaxed attitude. Draw inspiration from successful creative people around you.",
    4: "Enhance your reliability and punctuality by incorporating practical, organised, systematic approaches. Prioritise attention to details. Engage in outdoor and physical activities for self-discovery. Steer clear of procrastination.",
    5: "Embrace change and seek new experiences. Develop your communication skills and versatility. Travel, learn new skills, and stay curious. Your adaptability is your superpower.",
    6: "Focus on creating harmony in your home and relationships. Nurture your artistic side and beautify your environment. Practice unconditional love and service. Family bonds are your foundation.",
    7: "Deepen your spiritual practice and inner life. Spend time in solitude for reflection and study. Trust your powerful intuition. Explore metaphysical subjects and seek deeper meanings in life.",
    8: "Channel your ambition into structured, long-term goals. Develop financial intelligence and business acumen. Balance material pursuits with personal relationships. Your persistence will bring great rewards.",
    9: "Embrace your humanitarian impulses and serve a greater cause. Release what no longer serves you and make room for new experiences. Your compassion and wisdom inspire those around you.",
}

PERSONALITY_DATA = {
    1: "You project an image of confidence, authority and independence. People see you as a natural leader with a strong presence. Your pioneering spirit and bold approach to life make you stand out in any crowd.",
    2: "You project an image of gentleness, diplomacy and cooperation. People see you as a peacemaker and a good listener. Your warm, caring nature makes others feel comfortable and understood in your presence.",
    3: "Your energy radiates vitality and vibrancy. You possess a captivating and inspiring aura that uplifts those around you. Your charming nature and infectious personality make you a delight to be with. Your wit makes you the centre of attention.",
    4: "You project an image of reliability, stability and practicality. People see you as dependable and hardworking. Your methodical and organised approach to life gives others confidence that things will be done right.",
    5: "You possess a remarkable ability to stimulate and energize those around you. Social gatherings come alive in your presence as you infuse them with fresh and original ideas. Your conversations are characterized by a delightful blend of novelty, wit and charismatic charm.",
    6: "You project an image of warmth, nurturing and responsibility. People see you as caring, supportive and trustworthy. Your natural ability to create harmony and beauty makes you a beloved presence in any setting.",
    7: "You project an image of mystery, depth and intelligence. People are drawn to your quiet wisdom and introspective nature. Your analytical mind and spiritual depth give you an aura of profound understanding.",
    8: "You project an image of power, authority and success. People see you as ambitious, capable and in control. Your executive presence and business-like manner command respect and inspire confidence.",
    9: "You project an image of wisdom, compassion and universal love. People see you as inspiring, idealistic and deeply human. Your broad perspective and genuine concern for others makes you a natural humanitarian.",
}

SOUL_URGE_DATA = {
    1: "Deep desire to be independent and lead. Want to be first, original and self-sufficient. Crave recognition for unique accomplishments. Inner drive to stand on own two feet.",
    2: "Deep desire for love, harmony and connection. Want peace in all relationships. Crave partnership and belonging. Inner need to feel needed and appreciated.",
    3: "Deep desire to express yourself creatively. Want to entertain, inspire and uplift others. Crave social connection and joyful experiences. Inner need for appreciation of creative gifts.",
    4: "Want to be realistic, practical and intelligent. Want to create fixed assets and securities at earliest in life. Always want to remain organised. Want to be respected everywhere. Inner desire to serve others systematically.",
    5: "Deep desire for freedom and adventure. Want to experience everything life has to offer. Crave variety, travel and new experiences. Inner need to feel unrestricted and alive.",
    6: "Every penny is for family. Wants beautiful things in life. Wants to be cherished by family and close group of friends. Offers genuine help to others. Life sums up to Love, Friendship and Family.",
    7: "Deep desire for knowledge and spiritual truth. Want to understand the mysteries of life. Crave solitude and deep thinking. Inner need to find meaning beyond the material world.",
    8: "Deep desire for power, wealth and achievement. Want to build something lasting and significant. Crave recognition for accomplishments. Inner drive to succeed in material world.",
    9: "Deep desire to make the world a better place. Want to give freely and serve humanity. Crave universal love and acceptance. Inner need to live a life of meaning and purpose.",
}

FIRST_LETTER_DATA = {
    'A': "Natural leader with strong willpower. Independent, determined and ambitious. Highly creative with original ideas. Can be stubborn and self-centered at times. Strong drive to succeed on own terms.",
    'B': "Sensitive, cooperative and emotionally intuitive. Natural mediator with strong people skills. Deeply caring and devoted in relationships. Can be overly sensitive and indecisive.",
    'C': "Creative, expressive and optimistic. Wonderful communicator with a great sense of humor. Naturally social and uplifting to others. Can scatter energy and avoid difficult tasks.",
    'D': "Practical, disciplined and hardworking. Dependable and thorough in all endeavors. Strong builder with great organizational skills. Can be stubborn and resistant to change.",
    'E': "Versatile, freedom-loving and quick-minded. Excellent communicator and natural adventurer. Highly adaptable to new situations. Can be restless and inconsistent.",
    'F': "Responsible, caring and family-oriented. Natural nurturer with a strong sense of duty. Artistic and appreciates beauty. Can be self-sacrificing and worrisome.",
    'G': "Analytical, introspective and spiritually inclined. Deep thinker with strong intuition. Seeks perfection and truth. Can be secretive and overly critical.",
    'H': "Sociable, enjoyable to be around, and possessing notable intelligence. Highly prioritises freedom and independence. Remarkable sense of humour adds to their charm. Nurturing and empathetic towards others. Strong affinity for good music, food, drinks and art. Can become overly ambitious and selfish. Tires easily in physical activities.",
    'I': "Compassionate, artistic and highly sensitive. Deep humanitarian instincts. Strongly intuitive and emotionally aware. Can be moody and self-pitying.",
    'J': "Initiator with strong leadership qualities. Independent, determined and resourceful. Excellent at starting new projects. Can be impatient and domineering.",
    'K': "Highly cooperative with a charismatic personality. In touch with emotions and relies on intuition. Excels at entertaining others. Deep love for nurturing people and emotions. Ability to motivate and inspire. May encounter sudden events or losses. Fortunate financially with potential to become wealthy.",
    'L': "Analytical, detail-oriented and highly intelligent. Strong sense of justice and fairness. Excellent problem-solver. Can be overly critical and indecisive.",
    'M': "Hardworking, practical and deeply responsible. Strong maternal/paternal instincts. Highly reliable and dependable. Can be rigid and overly cautious.",
    'N': "Creative, intuitive and imaginative. Strong mental energy and quick thinking. Passionate and intense in pursuits. Can be nervous and unpredictable.",
    'O': "Responsible, compassionate and deeply committed. Strong sense of justice and fairness. Natural counselor and advisor. Can be self-righteous and overly cautious.",
    'P': "Intellectual, philosophical and spiritually aware. Seeks knowledge and deeper understanding. Strong powers of concentration. Can be secretive and isolated.",
    'Q': "Powerful, mysterious and highly intuitive. Strong leadership with unique perspectives. Excellent at reading situations. Can be suspicious and demanding.",
    'R': "Compassionate, humanitarian and deeply responsible. Strong work ethic and practical skills. Inspires others through example. Can be scattered and overly emotional.",
    'S': "Intense, emotional and highly magnetic. Natural initiator with strong willpower. Excellent at transformation and renewal. Can be secretive and obsessive.",
    'T': "Sensitive, intuitive and spiritually inclined. Natural healer and peacemaker. Strong sense of rhythm and creativity. Can be self-doubting and overly emotional.",
    'U': "Highly intuitive, humanitarian and universally minded. Strong spiritual awareness. Generous and compassionate. Can be impractical and escapist.",
    'V': "Practical, hardworking and highly capable. Excellent builder and organizer. Strong business instincts. Can be rigid and workaholic.",
    'W': "Versatile, communicative and highly social. Natural entertainer and storyteller. Quick-witted and adaptable. Can be scattered and superficial.",
    'X': "Intense, passionate and highly perceptive. Strong regenerative abilities. Excellent at research and investigation. Can be obsessive and secretive.",
    'Y': "Independent, spiritual and highly intuitive. Strong desire for freedom and truth-seeking. Natural philosopher. Can be indecisive and isolated.",
    'Z': "Optimistic, energetic and highly determined. Natural leader with infectious enthusiasm. Excellent at completing what others start. Can be impatient and domineering.",
}

SUCCESS_DATA = {
    1: {"qualities": "Leadership, originality and pioneering spirit define your success path. You have the drive to be first and blaze new trails. Your confidence and determination inspire others.", "challenges": "Avoid arrogance and learn to collaborate. Success grows when you empower others rather than dominating them."},
    2: {"qualities": "Diplomacy, cooperation and sensitivity are your keys to success. You excel in partnerships and create harmony wherever you go. Your intuition is a powerful guide.", "challenges": "Overcome indecisiveness and lack of confidence. Learn to stand firm in your own worth and value."},
    3: {"qualities": "Dynamic, creative and social. You convey the image of the joker, the entertainer and the mastermind of creativity. Your personality is characterised by humour, wit, intelligence and sociability. Inherently joyful, you spread happiness to those around you.", "challenges": "Fear of criticism or emotional baggage may suppress your dreams. The strong desire for social acceptance can lead you to compromise your remarkable creative abilities."},
    4: {"qualities": "Discipline, organization and practicality define your success. You build lasting foundations and see projects through to completion. Your reliability makes you invaluable.", "challenges": "Avoid rigidity and learn to adapt. Balance hard work with rest and relationships."},
    5: {"qualities": "Versatility, freedom and communication are your strengths. You adapt quickly and excel in dynamic environments. Your ability to connect with diverse people opens many doors.", "challenges": "Develop consistency and follow-through. Scattered energy and restlessness can undermine your many talents."},
    6: {"qualities": "Responsibility, nurturing and harmony define your success. You excel at creating beautiful, functional environments and caring for others. Your artistic sensibility and warm heart draw people to you.", "challenges": "Avoid martyrdom and learn healthy boundaries. Your tendency to sacrifice yourself for others can lead to resentment."},
    7: {"qualities": "Wisdom, analysis and spiritual insight are your success keys. You excel at research, investigation and finding hidden truths. Your depth of understanding gives you unique perspectives.", "challenges": "Avoid isolation and over-analysis. Share your insights with the world rather than keeping them to yourself."},
    8: {"qualities": "Ambition, authority and material mastery define your success. You excel at business, leadership and building financial security. Your executive abilities and determination create lasting achievements.", "challenges": "Avoid workaholism and ruthlessness. True success includes fulfilling personal relationships and good health."},
    9: {"qualities": "Compassion, wisdom and universal understanding are your greatest gifts. You inspire others through your idealism and generous spirit. Your broad perspective sees the big picture.", "challenges": "Avoid martyrdom and impracticality. Learn to complete projects and follow through on commitments."},
}

MATURITY_DATA = {
    1: "In your later years, you will increasingly value independence and self-reliance. A desire to lead and make your unique mark on the world will grow stronger. You may start new ventures or pursue long-held dreams with renewed determination.",
    2: "In your later years, relationships and emotional fulfillment will take center stage. You will seek deeper connections and meaningful partnerships. Your wisdom in diplomacy and understanding human nature will make you a valued counselor.",
    3: "In your later years, creative self-expression will become increasingly important. You will seek to express your authentic self through art, writing or communication. Your natural optimism and joy will radiate more strongly.",
    4: "As you enter later life, you will notice a shift towards practicality, organisation and concern for material achievements. You will turn ideas into practical realities. A deep desire for material success and respect persists. Legacy-building and strengthening family bonds become priorities. Avoid becoming rigid or overly work-focused.",
    5: "In your later years, freedom and adventure will remain important. You will seek new experiences and resist being tied down. Your adaptability will serve you well through life changes. Travel and learning keep your spirit young.",
    6: "In your later years, love, family and community will be your greatest sources of fulfillment. You will take on a nurturing, wise elder role. Creating beauty and harmony in your environment becomes deeply satisfying.",
    7: "As you mature, this number carries a philosophical and inherently wise energy. You will gradually let go of mundane aspects and expand mental horizons. Reading, contemplation and searching for Truths becomes central. Drawn to metaphysical subjects. Intuition sharpens. Need for privacy grows. Avoid excessive solitude.",
    8: "In your later years, the desire for achievement and material security intensifies. You will be drawn to positions of power and influence. Financial planning and building lasting legacy become central concerns. Balance ambition with wisdom.",
    9: "In your later years, humanitarian impulses and spiritual wisdom will come to full expression. You will be drawn to service, teaching and sharing your life wisdom. Letting go of the personal in favor of the universal brings deep peace.",
}

PERSONAL_YEAR_DATA = {
    1: {
        "title": "Year of New Beginnings, Fresh Starts and Independence",
        "positive": "New opportunities open up. Increased energy and motivation. Excellent for starting new projects, businesses or relationships. Seeds planted now will flourish.",
        "negative": "May feel restless and impatient. Risk of acting impulsively. Old structures may fall away causing temporary discomfort.",
        "luck": {"M1": 90, "M2": 70, "M3": 80, "M4": 60, "M5": 75, "M6": 65, "M7": 55, "M8": 70, "M9": 85},
    },
    2: {
        "title": "Year of Cooperation, Relationships and Patience",
        "positive": "Relationships deepen and flourish. Good year for partnerships and collaborations. Intuition is heightened. Emotional healing occurs.",
        "negative": "May feel overly sensitive or indecisive. Progress seems slow. Avoid confrontations and hasty decisions.",
        "luck": {"M1": 65, "M2": 90, "M3": 70, "M4": 75, "M5": 60, "M6": 85, "M7": 80, "M8": 55, "M9": 70},
    },
    3: {
        "title": "Year of Creativity, Expression and Social Expansion",
        "positive": "Creative energy is high. Social life flourishes. Excellent for artistic projects, communication and networking. Joy and optimism abound.",
        "negative": "Risk of scattering energy. May be superficial or avoid serious responsibilities. Watch spending.",
        "luck": {"M1": 80, "M2": 70, "M3": 90, "M4": 65, "M5": 75, "M6": 70, "M7": 60, "M8": 55, "M9": 85},
    },
    4: {
        "title": "Year of Stability, Security and Hard Work",
        "positive": "Will keep you in illusion for first 2 months then develop practicality. You become very practical. A sense of security will develop. Time to set a routine and build a system. Be aware and take care of your health.",
        "negative": "Low energy levels. Will feel pressurised. Days will go rigid and slow. You will be frustrated. Must do hard work to earn - cannot rely on luck.",
        "luck": {"M1": 100, "M2": 75, "M3": 70, "M4": 85, "M5": 60, "M6": 80, "M7": 65, "M8": 90, "M9": 55},
    },
    5: {
        "title": "Year of Change, Freedom and Adventure",
        "positive": "Exciting changes and new opportunities. Travel and new experiences. Increased freedom and flexibility. Dynamic energy brings breakthroughs.",
        "negative": "Instability and unpredictability. Difficulty maintaining routines. Risk of making hasty decisions. Scattered focus.",
        "luck": {"M1": 70, "M2": 60, "M3": 75, "M4": 65, "M5": 90, "M6": 55, "M7": 80, "M8": 70, "M9": 85},
    },
    6: {
        "title": "Year of Love, Family and Responsibility",
        "positive": "Family relationships strengthen. Home improvements and beautification. Opportunities for healing relationships. Creative and artistic endeavors flourish.",
        "negative": "Increased responsibilities and obligations. May feel burdened by demands of others. Avoid meddling in others affairs.",
        "luck": {"M1": 65, "M2": 85, "M3": 70, "M4": 75, "M5": 55, "M6": 90, "M7": 60, "M8": 70, "M9": 80},
    },
    7: {
        "title": "Year of Reflection, Spirituality and Inner Growth",
        "positive": "Deep spiritual insights and personal growth. Excellent for study, research and self-discovery. Intuition is very strong. Inner wisdom develops.",
        "negative": "May feel isolated or withdrawn. Material progress is slow. Avoid major financial decisions. Not a year for aggressive action.",
        "luck": {"M1": 55, "M2": 80, "M3": 65, "M4": 70, "M5": 75, "M6": 60, "M7": 90, "M8": 65, "M9": 85},
    },
    8: {
        "title": "Year of Power, Achievement and Financial Growth",
        "positive": "Career advancement and financial opportunities. Increased authority and recognition. Excellent for business expansion and investments. Hard work brings substantial rewards.",
        "negative": "Risk of overwork and burnout. Power struggles may arise. Avoid cutting corners or unethical shortcuts. Balance ambition with health.",
        "luck": {"M1": 75, "M2": 60, "M3": 65, "M4": 85, "M5": 70, "M6": 75, "M7": 55, "M8": 90, "M9": 70},
    },
    9: {
        "title": "Year of Completion, Release and Transformation",
        "positive": "Completion of long cycles. Letting go brings liberation. Humanitarian work is rewarding. Wisdom and compassion grow. Preparation for new cycle ahead.",
        "negative": "Endings can be painful. Must release what no longer serves. Avoid starting major new projects - this is a time of completion. Emotional intensity.",
        "luck": {"M1": 85, "M2": 70, "M3": 80, "M4": 60, "M5": 75, "M6": 70, "M7": 80, "M8": 65, "M9": 90},
    },
}

# ── Personal Month Data ────────────────────────────────────────────────────────
PERSONAL_MONTH_DATA = {
    1: {
        "positive": "Elevated levels of energy, strong determination, fresh prospects, burgeoning connections, wedlock, innovative and fruitful concepts, relocations, autonomy, action-driven, diverse streams of income, aspiration, and guidance.",
        "negative": "Aggressive, quarrelsome, careless, impatient, distressed, and suspicious.",
        "tips": "Embark on a new venture. Champion your unique ideas. Follow your instincts. Now is an opportune moment to seek assistance. Request a salary increase from your employer. Take action. Bring about that desired change. Submit an application for that fresh position. Promote yourself. Your success hinges on your drive. Embrace independence, assertiveness, and enthusiasm. Make swift decisions. Initiatives launched now will advance rapidly."
    },
    2: {
        "positive": "Amicable, affectionate, collaborative, tactful, unassuming, investigative, diplomatic, and perceptive.",
        "negative": "Temperamental, theatrical, emotional instability, dishonest, health issues, and anxiety.",
        "tips": "Embrace the role of a peacemaker. Employ diplomacy and tact to strengthen and harmonize friendships. Now is the opportune moment to gather what is rightfully owed to you. Avoid engaging in arguments. Strive to understand the other person's perspective. Show receptiveness, tolerance, and a good-natured attitude, radiating peace and harmony. Today is favorable for accumulation and analysis."
    },
    3: {
        "positive": "Charming, creative, entertainer, communicative, journeying, joyful, motivating, forging new friendships, and reuniting with old acquaintances.",
        "negative": "Self-centeredness, rumors, lack of focus, extravagant spending.",
        "tips": "Amuse your friends or business associates. Radiate charm and happiness to bring joy to others. Embrace your sense of humor. Express your creativity through writing, acting, painting, or music. Adopt a flexible attitude and embrace life as it unfolds. Indulge in enjoyable activities like playing bridge, golf, dancing, or attending the theatre."
    },
    4: {
        "positive": "Diligent, focused, pragmatic, systematic, and reliable.",
        "negative": "Lack of energy, stressed, inflexible, sluggish, and prone to frustration.",
        "tips": "Focus on and streamline your work, putting forth every effort to handle it methodically and efficiently. Practice thriftiness by initiating a bank account. Allocate time for routine and detailed tasks. Exercise self-discipline. Avoid beginning any new ventures. Accomplishing work with excellence will bring great satisfaction."
    },
    5: {
        "positive": "Sociable, advancement, career growth, adaptable, industrious, versatile, freedom-seeking, and pliable.",
        "negative": "Lacking focus, indifferent, erratic, and undependable.",
        "tips": "Spark the public's interest. Take swift action in an innovative manner. Spread enthusiasm by endorsing fresh concepts. Now is a propitious period to interact with the opposite sex. It's a favorable time for travel, buying, or selling goods. Embrace new opportunities with confidence, guided by your intuition."
    },
    6: {
        "positive": "Affection, matrimony, romantic, artistic, sociable, affectionate, considerate, caring, and harmonious.",
        "negative": "Unwilling to adapt, resistant to change, disagreements, self-centered, and volatile.",
        "tips": "Embrace responsibilities with grace. Enhance the environment at home, in the office, and within the community. Seek harmony and make adjustments for the comfort and happiness of all. Offer advice willingly but only when requested. This is a favorable period for purchasing, building, or leasing a home. Avoid engaging in unnecessary arguments."
    },
    7: {
        "positive": "Detail-oriented, economic security, insightful, contemplative, charismatic, and inquisitive. The middle of the month brings favorable circumstances.",
        "negative": "Quick-tempered, introverted, uncertain, and envious. Refrain from initiating new endeavors.",
        "tips": "Refine and perfect everything you are working on; add the final touches. Allocate some time for solitude — rest, relaxation, and focused contemplation. Pay heed to your intuitive inner voice. Avoid entering into partnerships on a 50-50 basis. This is a spiritually oriented time, and material success may not be at its peak."
    },
    8: {
        "positive": "Assertive, advancements, financial ventures, effective, courteous, benevolent, favorable outcomes from speculations, gains from real estate.",
        "negative": "Boisterous, covetous, and deceitful.",
        "tips": "Secure significant contracts and exude the aura of a powerful business executive. This period is ideal for executive-level decision-making, business expansion, and progress. Engage with major corporations or financial institutions. Consider investing in stable and reputable securities. Render substantial services, and you will reap bountiful rewards."
    },
    9: {
        "positive": "Compassionate, open-minded, secluded, fresh acquaintances, journeys of significance, and forgiving.",
        "negative": "Unmindful, ongoing disputes, hasty, unfeeling, distant, and criminal behavior.",
        "tips": "Assess your belongings and organize unfinished tasks, preparing for a fresh start tomorrow. Foster universal love and fraternity. Seek aspects to admire, appreciate, or praise in others. Resolve conflicts and take responsibility for any lingering challenges. This is an excellent period to embark on a long journey and foster meaningful connections."
    },
}

# ── Personal Day Data ──────────────────────────────────────────────────────────
PERSONAL_DAY_DATA = {
    1: {
        "text": "The day brimming with fresh aspirations, crafting novel strategies, and putting them into action.",
        "social_hints": "Embrace uniqueness and originality in your attire. Consider donning stripes and plaids to add a touch of individuality to your outfit.",
        "lucky_colors": "Orange, Copper, Red, and Lilac"
    },
    2: {
        "text": "On this day, you have the opportunity to enhance your plans while managing your emotions and being mindful of any tendency to become overly sensitive.",
        "social_hints": "Maintain a calm, sophisticated, and reserved demeanor. Opt for subdued colors, but consider wearing yellow to uplift your spirits when feeling down.",
        "lucky_colors": "Yellow, Gold, White, and Salmon"
    },
    3: {
        "text": "Indulge in a day of shopping, clubbing, and partying, savoring every moment to the fullest. It's a favorable period for exploring your creative side and seeking entertainment.",
        "social_hints": "Prioritize comfort over style when dressing. Opt for clothing with lace, frills, and jewelry to accentuate your look. Choose pleasing and soft materials.",
        "lucky_colors": "Rose, Forest Green, Amber, and Wine Red"
    },
    4: {
        "text": "Today presents a favorable opportunity for real estate transactions. Additionally, trading activities have the potential to be quite profitable.",
        "social_hints": "Adopt a conservative, tidy, and precise dressing style. Opt for clothing with straight lines and dark colors.",
        "lucky_colors": "Grey, Blue, Green, Light Brown, and Turquoise"
    },
    5: {
        "text": "Prepare yourself for unforeseen adventures, travel, and fresh opportunities. It is also an auspicious period for promoting new and innovative ideas.",
        "social_hints": "Embrace the role of a fashion trendsetter, donning sports attire. Cultivate your wit and sparkle as a captivating conversationalist.",
        "lucky_colors": "Pink, Blue, Red, and Turquoise"
    },
    6: {
        "text": "Today is dedicated to domestic affairs and responsibilities. However, refraining from engaging in arguments will work in your favor.",
        "social_hints": "Prioritize comfort over style in your attire, and opt for artistic clothes with soft lines. This is a time to focus on domestic matters.",
        "lucky_colors": "Yellow, Mustard, Red, and Navy Blue"
    },
    7: {
        "text": "Today is dedicated to nurturing your spiritual and mental well-being. Take time to rest and prioritize your health.",
        "social_hints": "Exude an air of reservation, refinement, and unapproachability. Dress in exclusive clothes with exquisite and distinct designs, favoring pastel colors.",
        "lucky_colors": "Violet, Magenta, Purple, and Turquoise"
    },
    8: {
        "text": "Today holds a higher likelihood of receiving delayed cheques, payments, or long-awaited good news. Material rewards and happiness may come your way on this day.",
        "social_hints": "Present an image of wealth and influence. Establish connections with prominent individuals. Purchase clothing that exudes a sense of luxury.",
        "lucky_colors": "Blue, Tan, Gold, Beige, and Grey"
    },
    9: {
        "text": "Make the most of this day by indulging in your favorite music, tidying up the house, and resolving any lingering issues with others.",
        "social_hints": "This is a time for love and affection. Perform a kind deed, and your rewards will multiply. Embrace a charming and lovable demeanor.",
        "lucky_colors": "Green, White, Red, Olive, Gold, and Lavender"
    },
}

# ── Lo Shu Arrows ──────────────────────────────────────────────────────────────
LOSHU_ARROWS = [
    {
        "name": "Arrow of Intellect",
        "numbers": [4, 9, 2],
        "strength": "A sharp and analytical mind. You possess intellectual brilliance and a strong memory. Learning comes naturally, and you excel in research and problem-solving.",
        "isolation": "Concentration and academic study may require extra effort. Patience and regular mental exercises will strengthen your intellectual abilities over time."
    },
    {
        "name": "Arrow of Will",
        "numbers": [3, 5, 7],
        "strength": "Exceptional determination and willpower. Once you set your sights on a goal, you pursue it with unwavering focus. Obstacles only strengthen your resolve.",
        "isolation": "Prone to self-doubt and wavering decisions. Developing clear, written goals and daily commitment practices is a transformative life lesson for you."
    },
    {
        "name": "Arrow of Activity",
        "numbers": [8, 1, 6],
        "strength": "Naturally active and practical. You thrive on turning ideas into reality through direct, sustained action. Inactivity is uncomfortable for you.",
        "isolation": "There may be a tendency to overthink rather than act. Success comes when you consciously push yourself to take concrete, consistent steps forward."
    },
    {
        "name": "Arrow of Practicality",
        "numbers": [4, 3, 8],
        "strength": "Highly skilled at manual, physical, and hands-on tasks. Grounded, hardworking, with an exceptional ability to build things that last.",
        "isolation": "Physical and routine tasks may feel draining. Structured routines, delegation, and working in short focused sessions will be very helpful."
    },
    {
        "name": "Arrow of Determination",
        "numbers": [9, 5, 1],
        "strength": "Exceptionally strong-willed and focused. An outstanding planner with the drive to see things through. You are a natural achiever in everything you commit to.",
        "isolation": "Planning and staying on course can be difficult. Seek mentors, use accountability partners, and break large goals into small daily actions."
    },
    {
        "name": "Arrow of Compassion",
        "numbers": [2, 7, 6],
        "strength": "Deep empathy and emotional intelligence. A natural healer and counselor, profoundly attuned to the needs of others. People feel safe in your presence.",
        "isolation": "Emotional connection with others may need conscious development. Practising active listening and empathy exercises will open new depths of relationship."
    },
    {
        "name": "Arrow of the Planner",
        "numbers": [4, 5, 6],
        "strength": "An excellent long-term planner and organizer. You create systems and structures that stand the test of time. Your methodical approach ensures lasting achievement.",
        "isolation": "Long-term planning may feel elusive. Focus on small, daily actions that accumulate toward larger goals, and review progress weekly."
    },
    {
        "name": "Arrow of Resilience",
        "numbers": [2, 5, 8],
        "strength": "Remarkable inner strength to recover from any setback. You learn from hardship and emerge stronger. Financially and emotionally, you are built to endure.",
        "isolation": "Setbacks may feel overwhelming. Building a spiritual practice, a strong support network, and celebrating small wins will build your inner resilience."
    },
]

# ── Lo Shu Planes ─────────────────────────────────────────────────────────────
LOSHU_PLANES = [
    {"name": "Thought Plane",   "numbers": [4, 9, 2], "description": "How you think, learn and process information"},
    {"name": "Will Plane",      "numbers": [3, 5, 7], "description": "Your drive, determination and inner willpower"},
    {"name": "Action Plane",    "numbers": [8, 1, 6], "description": "How you take action in the physical world"},
    {"name": "Spiritual Plane", "numbers": [4, 3, 8], "description": "Your spiritual nature, memory and physical vitality"},
    {"name": "Soul Plane",      "numbers": [9, 5, 1], "description": "Your emotional depth and intuitive nature"},
    {"name": "Practical Plane", "numbers": [2, 7, 6], "description": "Your practical, material and creative abilities"},
]

# ── Lo Shu Special Combinations ───────────────────────────────────────────────
LOSHU_SPECIAL_COMBOS = [
    {
        "condition": {3: 1, 1: 2},
        "label": "Detail-Oriented & Critical",
        "text": "Detail-oriented. Their habit of focusing on minute details tends to bring their attention to imperfections, making them find faults in others and correct them."
    },
    {
        "condition": {9: 2, 3: 1},
        "label": "Must Prove Themselves Right",
        "text": "Must prove themselves right in every situation. This can lead to disagreements and arguments as they prioritise proving their point over reaching a harmonious conclusion."
    },
    {
        "condition": {9: 2, 7: 1},
        "label": "Logical & Spiritually Gifted",
        "text": "Logical and gifted with a spiritual bent of mind. They believe whatever happens, happens for their highest good."
    },
    {
        "condition": {7: 1, 1: 2},
        "label": "Fascinated by Mystery",
        "text": "Fascinated by mystery. The unknown captivates and intrigues them."
    },
    {
        "condition": {5: 2, 7: 1},
        "label": "Learns & Earns from Skills",
        "text": "Encouraged to learn new skills. They have the ability to earn from the knowledge they acquire."
    },
    {
        "condition": {4: 1, 2: 1, 5: 2, 8: 1},
        "label": "Business Acumen & Property",
        "text": "Great in business. They usually invest in and acquire a lot of property."
    },
    {
        "condition": {2: 2, 7: 2, 1: 1},
        "label": "Sentimental & Often Cheated",
        "text": "Very sentimental and emotional. Unfortunately, they are often cheated during their life."
    },
    {
        "condition": {4: 2, 8: 2},
        "label": "Mind Power, Hard to Monetize",
        "text": "Blessed with good mind power, however, they will find themselves not able to monetize it, which leads to further struggle."
    },
    {
        "condition": {9: 1, 2: 3},
        "label": "Easily Influenced",
        "text": "Easily influenced by others and often seen to lose focus and fall into the trap of distraction."
    },
    {
        "condition": {9: 1, 5: 2, 1: 2, 6: 1},
        "label": "Rich Lifestyle, Materialistic",
        "text": "Lead a rich lifestyle and thus become attracted to materialistic things."
    },
]

LOSHU_INTERPRETATIONS = {
    1: {1: "Self-confident, expressive and vocal. Good communication skills. Natural ability to connect with others.", 2: "Strong communicator but may sometimes overexplain. Good at influencing others through words.", 3: "Difficulty vocalizing thoughts despite strong opinions. May attract conflicts through speech. Tendency to overexplain. Hard to say no. Can become dependent on others."},
    2: {1: "Balanced intuition and emotional sensitivity. Good family values and relationships.", 2: "Very family-oriented - family is everything. Highly intuitive with almost always correct instincts. Sensitive and emotionally driven.", 3: "Extremely sensitive and emotional. May be overly dependent on family. Strong psychic abilities but can be overwhelmed by emotions."},
    3: {1: "Sharp-minded, creative and knowledgeable. Exemplary imagination. Learns fast and plans efficiently. May experience delay in success but gets there eventually. Both business and job suit equally.", 2: "Highly creative with strong intellectual capabilities. Excellent planner and executor of ideas.", 3: "Exceptional creativity and intelligence. Natural teacher and knowledge-sharer. May become impatient with slower minds."},
    4: {1: "Practical and hardworking. Excellent hand-related skills like cooking, sewing, coding, playing instruments. Gets unique revolutionary ideas. Proficient in debates. Law is suitable career. Believes in multiple income sources. Dislikes grey areas.", 2: "Very practical and disciplined. Strong financial instincts and investment mindset.", 3: "Extremely hardworking but may become rigid. Exceptional practical skills. Must balance work with rest."},
    5: {1: "Balanced personality. Good connector between different areas of life. Practical and adaptable.", 2: "Strong mediating abilities. Excellent at balancing opposing forces. Natural diplomat.", 3: "Extremely versatile but may lack direction. Exceptional communication skills. Needs to focus energy productively."},
    6: {1: "Artistic sensibilities and appreciation for beauty. Caring and family-oriented. Good financial instincts.", 2: "Strong creative abilities and aesthetic sense. Very nurturing and family-devoted.", 3: "Exceptional artistic talent. Extremely family-focused. May neglect own needs for others. Strong healing abilities."},
    7: {1: "Blessed with intuitive powers that guide down right path. Family and children supportive. Respects all relationships. Always learns from mistakes. Dissatisfaction and heartbreaks likely in one area. Spirituality will knock early.", 2: "Very spiritually inclined. Strong intuition and healing abilities. Deep bond with family.", 3: "Exceptional spiritual gifts. May feel caught between material and spiritual worlds. Powerful healer and mystic."},
    8: {1: "Good financial awareness and practical wisdom. Learns valuable life lessons through hardships.", 2: "Strong financial acumen and business sense. Excellent at managing resources.", 3: "Exceptional material success potential. Very disciplined and ambitious. May become overly focused on material gain."},
    9: {1: "Highly ambitious from early age with immense willpower. Kind and helps others selflessly. Prefers giving orders over taking them. Forgives but never forgets insults. Promised high energy for any task.", 2: "Very humanitarian and generous. Strong leadership qualities. High energy and ambition.", 3: "Enjoys being appreciated. Straightforward and very generous with humanitarian intentions. May overlook opinions of others. Needs to channel energy surges through physical activities."},
}

MISSING_NUMBER_DATA = {
    1: {"impact": "No ego, low self-confidence, introverted, problems expressing experiences, face career problems.", "remedy_day": "Sunday", "remedy": "Donate Jaggery. Wear: Bloodstone + Tiger Eye bracelet. Chant: Om Shreem Suryay Namh. Yantra: Surya Yantra. Rudraksh: 1 Mukhi & 12 Mukhi."},
    2: {"impact": "Problems in love relations, lack of stability and patience, live in imaginations, lack of intuition and self-confidence.", "remedy_day": "Monday", "remedy": "Donate white things. Wear: Mother of Pearl + Howlite bracelet. Chant: Om shram shreem shraum sah chandramasaye namah. Yantra: Chandra Yantra. Rudraksh: 2 Mukhi."},
    3: {"impact": "Less grace of Guru and lord, problems in promotion and growth, lack of creative thinking, low self-confidence, easily distracted.", "remedy_day": "Thursday", "remedy": "Donate Yellow things. Wear: Natural Turquoise + Natural Amazonite bracelet. Chant: Om Gram greem groum sah gurave naman. Yantra: Guru Yantra. Rudraksh: 5 Mukhi."},
    4: {"impact": "Lack of financial stability and growth, lack of intuition power, struggle to achieve success, becomes directionless, weak thought power.", "remedy_day": "Saturday", "remedy": "Donate Black things and alcohol (to reduce its effect). Wear: Black Agate + 7 chakra bracelet. Chant: Om bhram bhreem bhroum sah rahave namah. Yantra: Rahu Yantra. Rudraksh: 5 Mukhi."},
    5: {"impact": "Lack of stability and self-confidence, health problems related to stomach and back pain, trouble starting work, loss in business, problem making own house.", "remedy_day": "Wednesday", "remedy": "Donate Green things, Ghee, study material, teach free of cost. Wear: Green Zade + Green Aventurian bracelet. Chant: Om bram breem broum sah budhaya Namah. Yantra: Buddh Yantra. Rudraksh: 10 Mukhi."},
    6: {"impact": "Lack of money and luxury life, struggle to achieve success, shortage of good friends, family support not available at right time, problems in love relations due to introverted nature.", "remedy_day": "Friday", "remedy": "Donate perfumes, cashew and cosmetics. Wear: Rose Quartz + Dragon Vein bracelet. Chant: Om dram dreem droum sah shukraya namah. Yantra: Shukra Yantra. Rudraksh: 9 Mukhi."},
    7: {"impact": "Hindrance in work and studies, no family support, no success despite effort, struggle more than success, mental disturbance.", "remedy_day": "Wednesday", "remedy": "Donate Black Clothes and Blanket. Wear: Cat's Eye + Azurite bracelet. Chant: Om shram shreem shroum sah ketave namah (7000 times in 25 days). Yantra: Ketu Yantra. Rudraksh: 9 Mukhi."},
    8: {"impact": "Difficulty making financial decisions, no perfection in work, lack of motivation and stability, life has lots of ups and downs, poor health and wealth.", "remedy_day": "Saturday", "remedy": "Donate Chayadan and Mustard Oil. Wear: Amethyst + Black Agate bracelet. Chant: Om Pram Preem Prom sah shanayshcharaya namah. Yantra: Shani Yantra. Rudraksh: 7 Mukhi."},
    9: {"impact": "Lack of energy and drive, difficulty completing tasks, emotional volatility, challenges in humanitarian pursuits, disconnected from higher purpose.", "remedy_day": "Tuesday", "remedy": "Donate Red things and food to the poor. Wear: Red Coral + Carnelian bracelet. Chant: Om kram kreem kroum sah bhaumaya namah. Yantra: Mangal Yantra. Rudraksh: 3 Mukhi."},
}

CAREER_DATA = {
    (1,1): {"general": "Double Sun energy — extraordinary leadership and individuality. Natural pioneers with magnetic personalities.", "fields": "Entrepreneurship, Politics, Executive Management, Brand Building, Innovation", "strengths": "bold decision-making, original thinking, inspirational leadership", "challenges": "sharing credit, avoiding stubbornness"},
    (1,2): {"general": "Mulank 1 leaders with Bhagyank 2 cooperation. Balance between independence and teamwork.", "fields": "Diplomacy, HR Management, Counseling, Public Relations, Team Leadership", "strengths": "leading with empathy, building team harmony, diplomatic authority", "challenges": "overcoming indecisiveness, balancing independence with collaboration"},
    (1,3): {"general": "Mulank 1 pioneer with Bhagyank 3 creativity. Dynamic communicators and creative leaders.", "fields": "Media, Entertainment, Marketing, Creative Direction, Motivational Speaking", "strengths": "creative leadership, charismatic communication, innovative thinking", "challenges": "maintaining focus, avoiding scattered energy"},
    (1,4): {"general": "Mulank 1 individuals are natural leaders and innovators. Bhagyank 4 brings stability, discipline and practical approach.", "fields": "Business Management, Financial Planning, Project Management, Administration, Real Estate", "strengths": "leadership skills, practical approach, strong discipline", "challenges": "flexibility in changing environments, learning to delegate"},
    (1,5): {"general": "Mulank 1 leadership with Bhagyank 5 freedom and adaptability. Dynamic, versatile go-getters.", "fields": "Sales, Digital Marketing, Travel Industry, Media, Entrepreneurship", "strengths": "pioneering new ventures, adaptable leadership, excellent communication", "challenges": "consistency, avoiding impulsive decisions"},
    (1,6): {"general": "Mulank 1 independence with Bhagyank 6 nurturing. Leaders who build communities and care for others.", "fields": "Healthcare Administration, Education Leadership, Social Enterprise, Luxury Brands, Interior Design", "strengths": "empathetic leadership, community building, aesthetic vision", "challenges": "setting boundaries, avoiding martyrdom"},
    (1,7): {"general": "Mulank 1 pioneer with Bhagyank 7 wisdom. Leaders with deep analytical and spiritual insight.", "fields": "Research, Philosophy, Technology, Spiritual Leadership, Academia", "strengths": "original research, visionary thinking, deep analysis", "challenges": "sharing findings openly, practical implementation"},
    (1,8): {"general": "Mulank 1 ambition with Bhagyank 8 material mastery. Born for power and business success.", "fields": "Business Leadership, Finance, Real Estate, Investment, Corporate Law", "strengths": "executive power, financial acumen, determined achievement", "challenges": "work-life balance, avoiding ruthlessness"},
    (1,9): {"general": "Mulank 1 leadership with Bhagyank 9 humanitarian service. Leaders who change the world.", "fields": "NGO Leadership, Politics, Humanitarian Work, Social Reform, Philanthropy", "strengths": "inspiring leadership, compassionate vision, global perspective", "challenges": "practicality, follow-through on commitments"},
    (2,1): {"general": "Mulank 2 sensitivity with Bhagyank 1 leadership. Diplomatic leaders with strong emotional intelligence.", "fields": "Counseling, Human Resources, Diplomatic Service, Psychology, Mediation", "strengths": "emotional intelligence, diplomatic leadership, strong intuition", "challenges": "assertiveness, overcoming indecisiveness"},
    (2,2): {"general": "Double Moon energy — deeply intuitive, empathetic and relationship-focused.", "fields": "Counseling, Nursing, Social Work, Teaching, Creative Arts", "strengths": "deep empathy, intuition, harmony-building, emotional support", "challenges": "setting boundaries, developing self-confidence"},
    (2,3): {"general": "Mulank 2 expression with Bhagyank 3 creativity. Harmonious creative collaborators.", "fields": "Art, Music, Writing, Event Planning, Community Development", "strengths": "creative collaboration, emotional expression, social harmony", "challenges": "self-promotion, consistency in creative output"},
    (2,4): {"general": "Mulank 2 sensitivity with Bhagyank 4 practicality. Emotionally intelligent builders.", "fields": "Accounting, Administrative Management, Social Planning, Education, Project Coordination", "strengths": "careful planning, emotional sensitivity, reliable execution", "challenges": "speaking up, developing assertiveness"},
    (2,5): {"general": "Mulank 2 diplomacy with Bhagyank 5 versatility. Adaptable communicators.", "fields": "Public Relations, Tourism, Language Services, Writing, Customer Relations", "strengths": "communication, adaptability, emotional intelligence", "challenges": "commitment, avoiding over-sensitivity"},
    (2,6): {"general": "Mulank 2 nurturing with Bhagyank 6 responsibility. Natural caregivers and community builders.", "fields": "Healthcare, Education, Social Work, Family Counseling, Non-profit", "strengths": "deep empathy, family-centered service, nurturing leadership", "challenges": "self-care, setting healthy boundaries"},
    (2,7): {"general": "Mulank 2 intuition with Bhagyank 7 wisdom. Deeply spiritual and psychic individuals.", "fields": "Psychology, Healing Arts, Research, Spiritual Counseling, Philosophy", "strengths": "psychic intuition, deep analysis, spiritual guidance", "challenges": "practical application, avoiding isolation"},
    (2,8): {"general": "Mulank 2 sensitivity with Bhagyank 8 ambition. Emotionally intelligent business minds.", "fields": "Financial Counseling, HR Leadership, Wellness Business, Real Estate, Luxury Services", "strengths": "emotional intelligence in business, relationship-based success, intuitive financial sense", "challenges": "decisiveness, asserting authority"},
    (2,9): {"general": "Mulank 2 harmony with Bhagyank 9 service. Compassionate helpers dedicated to humanity.", "fields": "Social Work, Healing Arts, Non-profit Management, Teaching, International Aid", "strengths": "deep compassion, collaborative service, emotional healing", "challenges": "practical boundaries, avoiding martyrdom"},
    (3,1): {"general": "Mulank 3 creativity with Bhagyank 1 leadership. Charismatic creative leaders.", "fields": "Entertainment, Media, Marketing, Brand Strategy, Public Speaking", "strengths": "creative leadership, charisma, original communication", "challenges": "follow-through, maintaining discipline"},
    (3,2): {"general": "Mulank 3 expression with Bhagyank 2 cooperation. Creative collaborators with strong social skills.", "fields": "Art Therapy, Creative Collaboration, Community Arts, Writing, Performance", "strengths": "expressive creativity, team harmony, social charm", "challenges": "self-confidence, avoiding over-dependence on approval"},
    (3,3): {"general": "Double Jupiter energy — extraordinarily gifted communicators and creative thinkers.", "fields": "Writing, Performing Arts, Comedy, Broadcasting, Education", "strengths": "exceptional communication, infectious enthusiasm, creative brilliance", "challenges": "focus, avoiding superficiality"},
    (3,4): {"general": "Mulank 3 creativity with Bhagyank 4 practicality. Creative individuals who build lasting work.", "fields": "Architecture, Design, Publishing, Content Strategy, Educational Materials", "strengths": "creative discipline, structured expression, reliable creativity", "challenges": "avoiding rigid thinking, balancing freedom and structure"},
    (3,5): {"general": "Mulank 3 expression with Bhagyank 5 freedom. Dynamic communicators who love variety.", "fields": "Journalism, Travel Writing, Digital Content, Marketing, Advertising", "strengths": "versatile communication, adaptable creativity, engaging storytelling", "challenges": "consistency, depth over breadth"},
    (3,6): {"general": "Mulank 3 creativity with Bhagyank 6 love and beauty. Artistic creators who bring beauty to life.", "fields": "Interior Design, Fashion, Music, Art, Lifestyle Blogging", "strengths": "aesthetic creativity, warm expression, beauty-centered work", "challenges": "business acumen, valuing own work"},
    (3,7): {"general": "Mulank 3 individuals are creative, expressive and communicative. Bhagyank 7 brings intuition, spirituality and analytical depth.", "fields": "Content Creation for Spirituality, Holistic Healing Practitioner, Spiritual Counselling, Creative Writing/Authorship, Media Production", "strengths": "creative spirituality, intuitive problem solving, effective communication", "challenges": "balancing practicality and idealism, managing emotional depth"},
    (3,8): {"general": "Mulank 3 creativity with Bhagyank 8 ambition. Creative entrepreneurs with business acumen.", "fields": "Entertainment Business, Publishing, Creative Agency, Brand Management, Media Production", "strengths": "creative business sense, charismatic authority, expressive leadership", "challenges": "work-life balance, avoiding overcommitment"},
    (3,9): {"general": "Mulank 3 expression with Bhagyank 9 service. Creative humanitarians who inspire through art.", "fields": "Humanitarian Arts, Activism, Social Media, Teaching, Cultural Programs", "strengths": "inspiring communication, creative compassion, artistic service", "challenges": "practical follow-through, financial management"},
    (4,1): {"general": "Mulank 4 discipline with Bhagyank 1 independence. Practical pioneers who build lasting innovations.", "fields": "Engineering, Technology, Architecture, Business Founding, Project Management", "strengths": "disciplined innovation, practical leadership, structured building", "challenges": "flexibility, embracing new approaches"},
    (4,2): {"general": "Mulank 4 practicality with Bhagyank 2 harmony. Reliable team players who build stable structures.", "fields": "Accounting, Administrative Management, Social Planning, Education, Healthcare Administration", "strengths": "organized reliability, team support, careful planning", "challenges": "assertiveness, adaptability"},
    (4,3): {"general": "Mulank 4 stability with Bhagyank 3 creativity. Systematic creative workers.", "fields": "Graphic Design, Technical Writing, Educational Content, Music Production, Architecture", "strengths": "structured creativity, reliable execution, planned innovation", "challenges": "spontaneity, avoiding over-analysis"},
    (4,4): {"general": "Double Rahu energy — unconventional, practical and intensely hardworking.", "fields": "Technology, Engineering, Finance, Research, Real Estate", "strengths": "exceptional discipline, innovative thinking, strong work ethic", "challenges": "rigidity, avoiding workaholism"},
    (4,5): {"general": "Mulank 4 structure with Bhagyank 5 freedom. Practical adventurers who bring order to change.", "fields": "Travel Industry, Technology, Sales, Project Management, Consulting", "strengths": "organized adaptability, practical communication, structured flexibility", "challenges": "embracing uncertainty, avoiding rigidity"},
    (4,6): {"general": "Mulank 4 discipline with Bhagyank 6 nurturing. Practical caregivers and reliable community builders.", "fields": "Healthcare Administration, Education, Social Services, Family Business, Real Estate", "strengths": "reliable care, practical nurturing, organized service", "challenges": "emotional openness, work-life balance"},
    (4,7): {"general": "Mulank 4 practicality with Bhagyank 7 wisdom. Deep thinkers who build knowledge systems.", "fields": "Research, Academia, Technology, Philosophy, Data Analysis", "strengths": "analytical depth, structured research, practical wisdom", "challenges": "social connection, sharing findings"},
    (4,8): {"general": "Mulank 4 discipline with Bhagyank 8 ambition. Powerhouses of business success.", "fields": "Finance, Real Estate, Business Management, Investment, Corporate Strategy", "strengths": "exceptional financial discipline, strategic planning, powerful execution", "challenges": "flexibility, work-life balance"},
    (4,9): {"general": "Mulank 4 practicality with Bhagyank 9 service. Systematic humanitarians who build lasting change.", "fields": "Non-profit Management, Social Entrepreneurship, Development Work, Education, Healthcare", "strengths": "organized service, practical compassion, systematic change-making", "challenges": "emotional flexibility, avoiding rigidity in service"},
    (5,1): {"general": "Mulank 5 freedom with Bhagyank 1 leadership. Dynamic, adventurous pioneers.", "fields": "Entrepreneurship, Media, Travel, Sales, Technology", "strengths": "bold adaptability, pioneering communication, adventurous leadership", "challenges": "consistency, long-term commitment"},
    (5,2): {"general": "Mulank 5 versatility with Bhagyank 2 cooperation. Flexible, socially-skilled communicators.", "fields": "Public Relations, Customer Success, Tourism, Language, Mediation", "strengths": "adaptable diplomacy, excellent communication, social intelligence", "challenges": "stability, avoiding over-sensitivity"},
    (5,3): {"general": "Mulank 5 freedom with Bhagyank 3 creativity. Extraordinarily communicative and expressive.", "fields": "Journalism, Content Creation, Broadcasting, Advertising, Stand-up Comedy", "strengths": "versatile creativity, engaging communication, social charisma", "challenges": "depth, following through on projects"},
    (5,4): {"general": "Mulank 5 adaptability with Bhagyank 4 stability. Organized adventurers who bring structure to change.", "fields": "Technology, Consulting, Project Management, Training, Sales Management", "strengths": "structured adaptability, practical communication, organized freedom", "challenges": "patience with slow processes, maintaining routines"},
    (5,5): {"general": "Double Mercury energy — extraordinarily versatile, communicative and freedom-loving.", "fields": "Media, Travel, Sales, Marketing, Entrepreneurship", "strengths": "exceptional adaptability, brilliant communication, adventurous spirit", "challenges": "commitment, avoiding restlessness"},
    (5,6): {"general": "Mulank 5 freedom with Bhagyank 6 responsibility. Adventurous nurturers who serve with variety.", "fields": "Travel Therapy, Health Coaching, Family Services, Education, Lifestyle Brand", "strengths": "warm adaptability, caring communication, service with creativity", "challenges": "stability, avoiding over-commitment"},
    (5,7): {"general": "Mulank 5 versatility with Bhagyank 7 wisdom. Freedom-seeking wisdom seekers.", "fields": "Philosophy, Research, Spiritual Travel, Writing, Teaching", "strengths": "versatile wisdom, intuitive communication, spiritual exploration", "challenges": "practical grounding, consistency"},
    (5,8): {"general": "Mulank 5 freedom with Bhagyank 8 ambition. Dynamic business builders who thrive on change.", "fields": "Sales Leadership, Business Development, Entrepreneurship, Finance, Media", "strengths": "dynamic business acumen, adaptable authority, excellent networking", "challenges": "discipline, avoiding scattered energy"},
    (5,9): {"general": "Mulank 5 freedom with Bhagyank 9 service. Adventurous humanitarians who serve diverse communities.", "fields": "International Aid, Social Media Activism, Travel Journalism, Community Outreach, Education", "strengths": "versatile compassion, cross-cultural communication, dynamic service", "challenges": "commitment, focusing humanitarian energy"},
    (6,1): {"general": "Mulank 6 nurturing with Bhagyank 1 leadership. Compassionate leaders who build communities.", "fields": "Healthcare Leadership, Education Administration, Social Enterprise, Luxury Hospitality, Interior Design", "strengths": "empathetic leadership, aesthetic vision, community building", "challenges": "assertiveness, avoiding over-responsibility"},
    (6,2): {"general": "Mulank 6 care with Bhagyank 2 harmony. Ultimate nurturers and peacemakers.", "fields": "Social Work, Counseling, Teaching, Healthcare, Family Services", "strengths": "deep nurturing, exceptional empathy, harmony creation", "challenges": "self-care, boundaries"},
    (6,3): {"general": "Mulank 6 beauty with Bhagyank 3 creativity. Artistic nurturers who create beautiful expressions.", "fields": "Fine Arts, Music, Interior Design, Fashion, Culinary Arts", "strengths": "artistic nurturing, aesthetic creativity, warm expression", "challenges": "business skills, self-promotion"},
    (6,4): {"general": "Mulank 6 responsibility with Bhagyank 4 discipline. Reliable builders of beautiful, stable homes.", "fields": "Real Estate, Architecture, Family Business, Education, Healthcare Administration", "strengths": "responsible building, practical beauty, reliable nurturing", "challenges": "emotional flexibility, avoiding perfectionism"},
    (6,5): {"general": "Mulank 6 nurturing with Bhagyank 5 adventure. Caring free spirits who serve with variety.", "fields": "Travel Therapy, Health Coaching, Creative Teaching, Lifestyle Brand, International Aid", "strengths": "adaptable nurturing, creative service, warm communication", "challenges": "stability, avoiding over-commitment"},
    (6,6): {"general": "Double Venus energy — extraordinary beauty, love, and nurturing capacity.", "fields": "Healthcare, Fine Arts, Interior Design, Education, Social Services", "strengths": "exceptional empathy, artistic mastery, devoted service", "challenges": "martyrdom, setting boundaries"},
    (6,7): {"general": "Mulank 6 love with Bhagyank 7 wisdom. Spiritually-gifted healers and advisors.", "fields": "Healing Arts, Spiritual Counseling, Psychology, Philosophy, Sacred Music", "strengths": "spiritual wisdom, healing love, deep intuition", "challenges": "practical business, avoiding isolation"},
    (6,8): {"general": "Mulank 6 responsibility with Bhagyank 8 ambition. Nurturing business leaders.", "fields": "Healthcare Business, Luxury Brand Management, Education Leadership, Social Enterprise, Real Estate", "strengths": "responsible ambition, aesthetic authority, nurturing leadership", "challenges": "work-life balance, avoiding over-control"},
    (6,9): {"general": "Mulank 6 care with Bhagyank 9 service. Ultimate humanitarian caregivers.", "fields": "International Aid, Social Work, Healing Centers, Environmental Activism, Teaching", "strengths": "universal compassion, dedicated service, healing wisdom", "challenges": "personal boundaries, practical sustainability"},
    (7,1): {"general": "Mulank 7 wisdom with Bhagyank 1 leadership. Visionary leaders with deep analytical insight.", "fields": "Research Leadership, Technology, Philosophy, Academic Leadership, Spiritual Direction", "strengths": "visionary analysis, pioneering research, deep leadership", "challenges": "sharing insights, social engagement"},
    (7,2): {"general": "Mulank 7 depth with Bhagyank 2 cooperation. Intuitive collaborators with spiritual gifts.", "fields": "Psychology, Spiritual Counseling, Research Partnerships, Healing Arts, Mediation", "strengths": "psychic intuition, collaborative wisdom, healing presence", "challenges": "assertiveness, practical grounding"},
    (7,3): {"general": "Mulank 7 analysis with Bhagyank 3 creativity. Intellectually creative and deeply expressive.", "fields": "Scientific Writing, Spiritual Arts, Philosophy, Research Communication, Metaphysical Teaching", "strengths": "analytical creativity, deep communication, spiritual expression", "challenges": "practical execution, social engagement"},
    (7,4): {"general": "Mulank 7 wisdom with Bhagyank 4 discipline. Systematic researchers and knowledge builders.", "fields": "Science, Research, Data Analysis, Engineering, Philosophy", "strengths": "analytical precision, systematic research, practical wisdom", "challenges": "social connection, emotional expression"},
    (7,5): {"general": "Mulank 7 depth with Bhagyank 5 freedom. Wisdom-seeking adventurers and free thinkers.", "fields": "Spiritual Travel, Research Journalism, Philosophy, Academic Exploration, Writing", "strengths": "versatile wisdom, intuitive communication, analytical exploration", "challenges": "practical grounding, commitment"},
    (7,6): {"general": "Mulank 7 wisdom with Bhagyank 6 love. Spiritual healers and wise caregivers.", "fields": "Healing Arts, Spiritual Psychology, Sacred Music, Philosophy, Family Therapy", "strengths": "wise compassion, spiritual healing, intuitive care", "challenges": "practical application, social boundaries"},
    (7,7): {"general": "Double Ketu energy — extraordinarily spiritual, analytical and mystical.", "fields": "Spirituality, Research, Philosophy, Occult Sciences, Healing", "strengths": "exceptional intuition, deep wisdom, spiritual mastery", "challenges": "practical grounding, avoiding isolation"},
    (7,8): {"general": "Mulank 7 wisdom with Bhagyank 8 ambition. Analytical achievers who build through insight.", "fields": "Investment Analysis, Strategic Consulting, Research Management, Technology Leadership, Finance", "strengths": "deep analytical business sense, intuitive strategy, wise authority", "challenges": "social engagement, work-life balance"},
    (7,9): {"general": "Mulank 7 spirituality with Bhagyank 9 service. Wise humanitarians and spiritual teachers.", "fields": "Spiritual Teaching, Philosophy, International Aid, Healing Centers, Metaphysical Writing", "strengths": "wise compassion, spiritual service, deep understanding", "challenges": "practical execution, grounding in material world"},
    (8,1): {"general": "Mulank 8 ambition with Bhagyank 1 leadership. Born for positions of ultimate power.", "fields": "Executive Leadership, Business Ownership, Investment, Politics, Real Estate", "strengths": "decisive authority, financial mastery, pioneering ambition", "challenges": "work-life balance, collaboration"},
    (8,2): {"general": "Mulank 8 power with Bhagyank 2 diplomacy. Powerful yet emotionally intelligent leaders.", "fields": "Diplomatic Business, HR Leadership, Financial Counseling, Luxury Services, Mediation", "strengths": "emotionally intelligent authority, diplomatic power, relationship-based business", "challenges": "decisiveness, balancing sensitivity with ambition"},
    (8,3): {"general": "Mulank 8 achievement with Bhagyank 3 creativity. Ambitious creative entrepreneurs.", "fields": "Entertainment Business, Publishing, Brand Management, Creative Agency, Media", "strengths": "creative business mastery, charismatic authority, expressive ambition", "challenges": "focus, avoiding overcommitment"},
    (8,4): {"general": "Mulank 8 power with Bhagyank 4 discipline. Ultimate business builders and financial masters.", "fields": "Finance, Real Estate, Corporate Strategy, Engineering, Investment Management", "strengths": "exceptional financial discipline, strategic planning, powerful execution", "challenges": "flexibility, interpersonal warmth"},
    (8,5): {"general": "Mulank 8 ambition with Bhagyank 5 freedom. Dynamic business builders who adapt and conquer.", "fields": "Sales Leadership, Business Development, Entrepreneurship, Technology, Media", "strengths": "adaptable ambition, powerful communication, dynamic business sense", "challenges": "consistency, avoiding scattered focus"},
    (8,6): {"general": "Mulank 8 authority with Bhagyank 6 nurturing. Powerful leaders who build caring organizations.", "fields": "Healthcare Business, Education Leadership, Social Enterprise, Luxury Brand, Real Estate", "strengths": "powerful nurturing, responsible authority, aesthetic business vision", "challenges": "personal boundaries, avoiding martyrdom"},
    (8,7): {"general": "Mulank 8 ambition with Bhagyank 7 wisdom. Strategic achievers with deep analytical insight.", "fields": "Investment Analysis, Strategic Consulting, Technology Leadership, Research Management, Finance", "strengths": "analytical authority, wise strategy, deep business acumen", "challenges": "social engagement, sharing insights"},
    (8,8): {"general": "Double Saturn energy — extraordinary material ambition, discipline and financial power.", "fields": "Finance, Real Estate, Corporate Leadership, Investment, Business Empire Building", "strengths": "exceptional financial mastery, powerful discipline, material achievement", "challenges": "personal relationships, avoiding ruthlessness"},
    (8,9): {"general": "Mulank 8 power with Bhagyank 9 service. Powerful humanitarians who fund and lead great causes.", "fields": "Philanthropic Leadership, Social Enterprise, NGO Management, Political Service, Impact Investment", "strengths": "powerful compassion, resource-driven service, ambitious humanitarianism", "challenges": "personal boundaries, avoiding martyrdom"},
    (9,1): {"general": "Mulank 9 passion with Bhagyank 1 leadership. Courageous leaders who inspire and transform.", "fields": "Social Leadership, Military, Sports, Entrepreneurship, Activism", "strengths": "passionate leadership, courageous pioneering, inspiring ambition", "challenges": "patience, avoiding aggression"},
    (9,2): {"general": "Mulank 9 energy with Bhagyank 2 harmony. Passionate diplomats who serve with sensitivity.", "fields": "Diplomacy, Conflict Resolution, Social Work, Sports Coaching, Community Leadership", "strengths": "passionate empathy, diplomatic energy, harmonious service", "challenges": "channeling aggression, emotional boundaries"},
    (9,3): {"general": "Mulank 9 fire with Bhagyank 3 creativity. Inspirational creative forces.", "fields": "Motivational Speaking, Creative Arts, Entertainment, Activism, Media", "strengths": "passionate creativity, inspirational communication, energetic expression", "challenges": "focus, avoiding impulsiveness"},
    (9,4): {"general": "Mulank 9 drive with Bhagyank 4 discipline. Systematic warriors who achieve through hard work.", "fields": "Military, Sports Training, Social Reform, Engineering, Community Building", "strengths": "disciplined passion, systematic drive, practical courage", "challenges": "flexibility, work-life balance"},
    (9,5): {"general": "Mulank 9 energy with Bhagyank 5 freedom. Dynamic, adventurous humanitarians.", "fields": "Social Activism, Travel, International Aid, Journalism, Sports", "strengths": "passionate adaptability, energetic communication, adventurous service", "challenges": "commitment, avoiding impulsiveness"},
    (9,6): {"general": "Mulank 9 passion with Bhagyank 6 love. Passionate caregivers who fight for others.", "fields": "Healthcare, Social Work, Education, Advocacy, Community Service", "strengths": "passionate nurturing, courageous care, loving service", "challenges": "personal boundaries, channeling anger productively"},
    (9,7): {"general": "Mulank 9 energy with Bhagyank 7 wisdom. Passionate spiritual warriors and wise teachers.", "fields": "Spiritual Activism, Philosophy, Healing Arts, Military History, Social Research", "strengths": "passionate wisdom, spiritual courage, energetic insight", "challenges": "patience, practical grounding"},
    (9,8): {"general": "Mulank 9 fire with Bhagyank 8 ambition. Intense achievers driven by passion and power.", "fields": "Business Leadership, Sports Management, Military, Finance, Social Enterprise", "strengths": "passionate ambition, courageous authority, intense achievement", "challenges": "anger management, work-life balance"},
    (9,9): {"general": "Double Mars energy — extraordinary passion, courage and humanitarian drive.", "fields": "Humanitarian Leadership, Military Service, Sports, Activism, Social Reform", "strengths": "exceptional courage, passionate service, powerful transformation", "challenges": "channeling aggression, practical sustainability"},
}

# ── Pinnacle Data ─────────────────────────────────────────────────────────────
PINNACLE_DATA = {
    1: {
        "title": "Pinnacle of Leadership & Independence",
        "text": "A period of self-discovery and personal development. You are called to step forward as an individual — to lead, initiate, and forge your own path. Confidence, originality, and self-reliance are the keys to success. Opportunities come through bold action and independent thinking. Seeds of ambition planted now will bear fruit in future cycles.",
        "themes": "Independence, Leadership, New Beginnings, Self-Reliance",
        "advice": "Trust your instincts. Don't wait for others' approval. Take the lead and initiate the changes you wish to see in your life."
    },
    2: {
        "title": "Pinnacle of Cooperation & Partnership",
        "text": "A quieter, more reflective period focused on relationships, cooperation, and emotional depth. Progress comes through patience and working harmoniously with others. Intuition is heightened, and meaningful partnerships — personal and professional — are your greatest source of support and growth. Small, steady steps accumulate into significant progress.",
        "themes": "Patience, Diplomacy, Partnerships, Emotional Growth",
        "advice": "Be patient and adaptable. Success comes through collaboration. Trust your intuition and nurture the relationships that matter most."
    },
    3: {
        "title": "Pinnacle of Creativity & Expression",
        "text": "A vibrant, socially rich period that brings opportunities for creative expression, communication, and joyful expansion. This is a time to shine — to share your talents, build your network, and express yourself fully. The arts, writing, speaking, and social activities are especially favoured. Optimism and a light-hearted approach attract remarkable opportunities.",
        "themes": "Creativity, Communication, Social Growth, Joy",
        "advice": "Express yourself freely and fully. Share your gifts with the world. Cultivate joy and let your personality attract the connections and opportunities you need."
    },
    4: {
        "title": "Pinnacle of Foundation & Hard Work",
        "text": "A period of building — laying the foundations of security, stability, and long-term success through sustained effort and discipline. The work done now creates structures that support you for decades. It may feel demanding at times, but every effort made is an investment in lasting achievement. Health, home, finances, and career all benefit from careful attention.",
        "themes": "Discipline, Hard Work, Stability, Foundation-Building",
        "advice": "Embrace routine, structure, and sustained effort. Focus on quality over shortcuts. The foundation you build now will support all future success."
    },
    5: {
        "title": "Pinnacle of Change & Freedom",
        "text": "A dynamic and unpredictable period that brings significant changes, new adventures, and an expanded sense of freedom. Flexibility, adaptability, and openness to new experiences are essential. Travel, new careers, new relationships, and exciting opportunities arise when you release attachment to the familiar and embrace the momentum of change.",
        "themes": "Change, Freedom, Adventure, Versatility",
        "advice": "Embrace change rather than resisting it. Stay flexible and open. The opportunities in this period come disguised as disruption — welcome them."
    },
    6: {
        "title": "Pinnacle of Family & Responsibility",
        "text": "A period centred on home, family, love, and community responsibility. You are called to nurture, support, and create harmony in your closest relationships. Meaningful domestic achievements — marriage, home, raising children, community service — bring profound fulfilment. Beauty, creativity, and a caring nature attract love and appreciation in all forms.",
        "themes": "Family, Love, Responsibility, Service, Harmony",
        "advice": "Embrace your responsibilities with love. Invest in your home and relationships. Your greatest fulfilment comes through serving those you love with an open heart."
    },
    7: {
        "title": "Pinnacle of Reflection & Inner Wisdom",
        "text": "A deeply introspective period that calls you inward. A time for study, spiritual development, deep thinking, and the cultivation of inner wisdom. Material ambitions take a back seat as the focus shifts to understanding — of yourself, of life, of the deeper patterns at work. Solitude, research, and contemplative practices are especially rewarding.",
        "themes": "Spirituality, Reflection, Wisdom, Study, Inner Growth",
        "advice": "Value quiet and solitude. Invest in knowledge, meditation, and inner development. Wisdom earned in this period becomes an enduring inner resource."
    },
    8: {
        "title": "Pinnacle of Achievement & Material Power",
        "text": "A powerful period of material achievement, career advancement, and financial growth. The ambitions and hard work of previous cycles now produce tangible rewards. Authority, recognition, and material success are hallmarks of this pinnacle. Business ventures, investments, and leadership roles are especially favoured. Apply yourself with discipline and integrity.",
        "themes": "Achievement, Career, Financial Growth, Authority, Recognition",
        "advice": "Think big and act decisively. Apply discipline and integrity to your ambitions. The rewards of this pinnacle are proportional to the effort and character you bring."
    },
    9: {
        "title": "Pinnacle of Completion & Humanitarian Service",
        "text": "A profoundly meaningful period of completion, wisdom, and service to others. You are called to release what no longer serves, to forgive, and to contribute to something larger than yourself. Compassion, tolerance, and a universal perspective define this time. Fulfilment comes not from personal gain but from the depth of your contribution to others.",
        "themes": "Completion, Compassion, Service, Wisdom, Universal Love",
        "advice": "Let go with grace. Give generously without expectation. Your purpose in this period is to be of service — and in that service, you will find profound fulfilment."
    },
}

# ── Challenge Data ─────────────────────────────────────────────────────────────
CHALLENGE_DATA = {
    0: {
        "title": "Challenge of All Choices",
        "text": "The 0 Challenge is rare and represents the challenge of choice itself. All doors are open, but the absence of a defining weakness means you must develop the wisdom to choose rightly. This can lead to indecision or a feeling of being lost. The path is to develop strong personal values and the courage to commit to them fully.",
        "lesson": "Develop clarity of values and the courage to commit to a chosen path despite having infinite options."
    },
    1: {
        "title": "Challenge of Self",
        "text": "The core challenge is to develop authentic confidence, independence, and assertiveness. You may struggle with over-dependence on others' opinions or — conversely — with aggressive overcompensation. The lesson is to find the middle path: genuine self-reliance that neither isolates nor dominates.",
        "lesson": "Develop genuine self-confidence. Learn to lead without aggression and to stand alone without isolation."
    },
    2: {
        "title": "Challenge of Sensitivity",
        "text": "You are naturally empathetic and sensitive, but the challenge lies in managing that sensitivity productively. Hypersensitivity, indecision, fear of confrontation, and difficulty setting emotional boundaries are the main obstacles. Honour your sensitivity as a gift while developing emotional resilience and the courage to be direct.",
        "lesson": "Honor your sensitivity while building emotional resilience. Learn to set boundaries and speak your truth with kindness."
    },
    3: {
        "title": "Challenge of Expression",
        "text": "The challenge of sharing your creativity, ideas, and personality fully and confidently. Self-doubt, self-criticism, and scattered energy can prevent you from fulfilling your creative potential. The lesson is to commit to a creative outlet, silence the inner critic, and share your gifts without waiting for perfection.",
        "lesson": "Silence self-doubt and express yourself freely. Choose one creative path and commit to it deeply."
    },
    4: {
        "title": "Challenge of Discipline",
        "text": "The challenge is to develop structure, patience, and consistent effort without becoming rigid or resistant to change. You may swing between overwork and inactivity, or struggle with practicality and routine. Build reliable habits that support long-term success without suffocating your natural spontaneity.",
        "lesson": "Build daily structure and discipline. Learn to work consistently without becoming rigid or resentful of routine."
    },
    5: {
        "title": "Challenge of Freedom",
        "text": "The challenge is to find healthy freedom without becoming irresponsible. Restlessness, overindulgence, and fear of commitment are the shadow sides of this number. The desire for constant change can undermine relationships, careers, and finances. The lesson is to embrace freedom within structure — adventurous but grounded.",
        "lesson": "Channel your love of freedom productively. Develop commitment and follow-through without sacrificing your adventurous spirit."
    },
    6: {
        "title": "Challenge of Responsibility",
        "text": "The challenge is a balanced relationship with responsibility — caring for others without martyrdom, and having high standards without perfectionism. You may take on too much and resent it, or struggle to accept help. Give generously from a full cup rather than an empty one.",
        "lesson": "Balance caring for others with caring for yourself. Release perfectionism and the need to control outcomes for those you love."
    },
    7: {
        "title": "Challenge of Trust",
        "text": "The challenge is to develop faith — in yourself, in others, and in life itself. Excessive skepticism, emotional withdrawal, and a tendency to isolate can prevent deep connection. The fear of being misunderstood or betrayed may keep you at a safe but lonely distance. Your depth is a gift — trust others enough to share it.",
        "lesson": "Develop faith and openness. Allow others to truly know you. Trust is the gateway to the depth of connection you seek."
    },
    8: {
        "title": "Challenge of Power",
        "text": "The challenge is to develop a healthy, balanced relationship with material power — money, authority, and ambition. Either the pursuit of power or the fear of it can create significant obstacles. Misuse of authority, materialism, or conversely sabotaging your own financial success, are common expressions. Use power ethically and with genuine generosity.",
        "lesson": "Develop a healthy relationship with money and authority. Use power in service of others and build success on a foundation of integrity."
    },
}

# ── Compatibility Data ─────────────────────────────────────────────────────────

COMPAT_MATRIX = {
    (1,1): 9, (1,2): 7, (1,3): 9, (1,4): 5, (1,5): 8, (1,6): 7, (1,7): 7, (1,8): 3, (1,9): 9,
    (2,2): 8, (2,3): 8, (2,4): 5, (2,5): 8, (2,6): 9, (2,7): 8, (2,8): 3, (2,9): 6,
    (3,3): 9, (3,4): 5, (3,5): 9, (3,6): 8, (3,7): 9, (3,8): 4, (3,9): 8,
    (4,4): 6, (4,5): 7, (4,6): 6, (4,7): 8, (4,8): 9, (4,9): 4,
    (5,5): 9, (5,6): 8, (5,7): 7, (5,8): 6, (5,9): 7,
    (6,6): 9, (6,7): 8, (6,8): 4, (6,9): 8,
    (7,7): 8, (7,8): 5, (7,9): 6,
    (8,8): 8, (8,9): 3,
    (9,9): 8,
}

COMPAT_PAIR_TEXT = {
    (1,1): "Two strong-willed leaders who understand each other's drive and ambition deeply. The key is avoiding power struggles — when you align your goals rather than compete, this pairing becomes unstoppable. Equal respect is everything.",
    (1,2): "The leader and the peacemaker complement each other beautifully. 1 provides direction and drive while 2 provides emotional depth and support. Some tension exists between independence and need for closeness, but this is a deeply rewarding balance.",
    (1,3): "Sun and Jupiter are cosmic friends, and it shows. Natural warmth, shared enthusiasm, and a mutual love of life make this a joyful and expansive pairing. You inspire each other to grow, lead, and create.",
    (1,4): "The pioneer meets the builder. 1 moves fast; 4 moves methodically. With respect for each other's pace, this pair can construct something truly remarkable and lasting together.",
    (1,5): "Both love freedom and action. 1 leads from ambition and 5 leads from curiosity — together you create an energetic, stimulating relationship full of adventure and fresh experiences.",
    (1,6): "Leadership meets love and nurturing. 1 drives ambition forward while 6 creates warmth at home. Deeply fulfilling when 1 slows down enough to appreciate what 6 builds, and 6 allows 1 their independence.",
    (1,7): "The doer and the thinker. 1 acts while 7 reflects. This creates a stimulating balance — 7's depth fascinates 1, and 7 is grounded by 1's decisiveness. Mutual respect for different approaches is key.",
    (1,8): "Sun and Saturn — a classic challenge. Both are powerful but operate at opposite frequencies. 1 seeks recognition; 8 seeks control. A deep karmic pairing that requires extraordinary mutual respect to thrive.",
    (1,9): "Two fire energies united. Sun and Mars create a passionate, courageous, and driven pairing. You share ambition, idealism, and the desire to make your mark on the world. Intensely compatible.",
    (2,2): "Double sensitivity creates profound emotional understanding — you intuitively sense each other's needs. The risk is over-sensitivity and co-dependence. Maintaining individual strength keeps this deep connection healthy.",
    (2,3): "Moon and Jupiter — a harmonious and nourishing pairing. 2 provides emotional warmth and 3 provides optimism and expansive energy. You naturally uplift each other and build a joyful shared life.",
    (2,4): "Emotion meets practicality. 2 seeks connection and 4 seeks security through work. When 4 expresses feelings and 2 appreciates 4's steady dedication, this becomes a deeply stable and trusting relationship.",
    (2,5): "Intuition meets versatility. 2's emotional depth complements 5's dynamic energy. 5 brings excitement into 2's world; 2 provides the emotional anchor that free-spirited 5 secretly needs.",
    (2,6): "One of the most naturally harmonious pairings. Moon and Venus are cosmic friends — both value love, family, and emotional depth. A deeply warm, nurturing, and mutually supportive relationship.",
    (2,7): "Deep emotional and spiritual resonance. Both 2 and 7 are intuitive, sensitive, and drawn to the unseen. This pairing creates a mystical, soulful connection built on unspoken understanding.",
    (2,8): "Sensitivity meets ambition. 2 needs emotional warmth; 8 leads with power. Saturn can feel cold to the Moon's needs. Deep growth is possible here, but requires significant patience and effort from both.",
    (2,9): "Empathy meets passion. 2's nurturing nature and 9's humanitarian fire create a loving and purposeful bond. The challenge is that 9 can be too intense and independent for 2's need for closeness.",
    (3,3): "Double Jupiter — an abundant, joyful, and creatively explosive pairing. You bring out each other's wit, enthusiasm, and social brilliance. The risk is over-indulgence and scattered energy, but this is a deeply happy union.",
    (3,4): "Creativity meets discipline. 3's expansive ideas and 4's practical execution can be a powerful team. Tension arises when 3 feels constrained and 4 feels overwhelmed by 3's pace — but together you're formidable.",
    (3,5): "Two of the most communicative numbers. Jupiter and Mercury are natural cosmic friends. You stimulate each other intellectually, love new experiences, and create a vibrant, joyful shared life.",
    (3,6): "Creative beauty. 3 expresses and 6 nurtures. Together you create an aesthetically rich, socially warm relationship. Both are loving and generous — a highly compatible and joyful pairing.",
    (3,7): "Wisdom and expression. 3 communicates outwardly; 7 contemplates deeply. When balanced, 3 gives 7 a reason to emerge, and 7 gives 3's ideas profound depth. A deeply enriching connection.",
    (3,8): "Jupiter and Saturn are natural opposites — expansion meets contraction. 3's optimism and 8's pragmatism can clash, but when harnessed together they create a remarkably balanced and successful partnership.",
    (3,9): "Two generous, expansive souls united by shared fire and enthusiasm. You inspire each other and share a love of life. Creative, passionate, and mutually supportive — a highly compatible pairing.",
    (4,4): "Double Rahu — unconventional and unpredictable. You understand each other's restless nature and non-conformist thinking. The challenge is grounding — two Rahu energies can scatter without shared structure.",
    (4,5): "The unconventional meets the versatile. Both 4 and 5 resist the ordinary. You understand each other's need for freedom from convention and can build an exciting, innovative life together.",
    (4,6): "Structure meets nurturing. 4 builds the foundation; 6 creates the home. A practical and loving pairing that works best when both appreciate what the other brings rather than trying to change each other.",
    (4,7): "Two introspective, analytical minds. Rahu and Ketu are complementary forces in Vedic astrology — shadow planets that balance each other. This creates a deep, unusual, and profoundly interesting connection.",
    (4,8): "Two of the most materially ambitious numbers. When aligned, Rahu and Saturn create extraordinary financial and business success. This is one of the most powerful pairings for shared practical ambition.",
    (4,9): "Rahu meets Mars — unconventional meets passionate. This pairing can produce remarkable innovation or significant conflict, depending on both individuals' maturity and willingness to meet each other halfway.",
    (5,5): "Double Mercury — the most versatile and communicative of all pairings. Two 5s create an endlessly stimulating, free, and adventurous relationship. You must consciously build roots together to sustain it.",
    (5,6): "Freedom meets responsibility. 5 needs change and exploration; 6 needs stability and family. With mutual respect, 5 brings excitement and 6 brings warmth — a beautifully complementary pairing.",
    (5,7): "Curiosity meets wisdom. 5's love of new experiences combines with 7's depth of knowledge. Both are drawn to understanding — 5 explores the outer world while 7 explores the inner. A stimulating and enriching bond.",
    (5,8): "Adaptability meets authority. 5 moves freely while 8 seeks control. With mutual respect, this pairing can build an exciting and financially successful life. The key is honouring each other's very different rhythms.",
    (5,9): "Two dynamic energies. Mercury and Mars create a stimulating, action-filled relationship. Both love freedom and excitement — a passionate and spirited pairing that thrives on growth and new adventures.",
    (6,6): "Pure Venus energy — the most loving and harmonious self-pairing. You both value beauty, family, and emotional depth equally. Deep understanding, mutual devotion, and a naturally beautiful shared life.",
    (6,7): "Love meets wisdom. Venus and Ketu create a beautifully balanced pairing — 6 brings warmth and connection while 7 brings depth and spiritual understanding. A quietly profound and deeply fulfilling union.",
    (6,8): "Nurturing meets ambition. 6's loving energy and 8's drive for success can be at odds. When 8 remembers to be present and 6 supports 8's ambition, this pairing achieves both love and material success.",
    (6,9): "Love meets passion. Venus and Mars create natural attraction. 6 nurtures and 9 inspires — a warm, passionate, and socially conscious relationship. One of the most romantically compatible pairings.",
    (7,7): "A rare and profound spiritual bond. You understand each other at the soul level without words. The risk is becoming too withdrawn together — outside connection and shared purpose help keep you balanced.",
    (7,8): "Spiritual meets material. Ketu seeks liberation while Saturn seeks accumulation — fundamentally different orientations. This pairing requires extraordinary mutual understanding and respect for different life priorities.",
    (7,9): "Spirituality meets passion. 7's reflective, inward energy is both attracted to and challenged by 9's outward-facing fire. An interesting and growth-producing pairing when both respect each other's nature.",
    (8,8): "Double Saturn — formidable. Two 8s together create an extraordinarily powerful pairing for shared ambition and business. Romantically, both need to consciously create warmth and emotional connection.",
    (8,9): "Saturn meets Mars — the most challenging pairing in numerology. Both are powerful and neither yields easily. Profound karmic lessons await here, but the friction rarely produces the harmony both truly desire.",
    (9,9): "Double Mars energy — passionate, powerful, and intense. You share the same humanitarian fire and ambition to make a difference. The challenge is managing two equally strong-willed energies without competition.",
}

RELATIONSHIP_NUMBER_DATA = {
    1: "Combined, you radiate independence and leadership. This relationship is defined by individual strength and shared ambition — at its best when both support each other's goals equally.",
    2: "Your combined energy creates a deeply sensitive, intuitive, and cooperative bond. Harmony and mutual support are the hallmarks of your relationship.",
    3: "Together you are a creatively explosive pair — joyful, communicative, and socially magnetic. Life is more vibrant and fun when you're together.",
    4: "Your relationship creates a foundation of stability, hard work, and long-term security. You are building something real and lasting together.",
    5: "Combined, you create a dynamic, freedom-loving, and adventurous union. Change and variety keep your relationship alive and exciting.",
    6: "Your relationship vibrates with love, responsibility, and beauty. Family, home, and creating a harmonious life together are central themes.",
    7: "Together you enter a realm of depth, mystery, and spiritual growth. This is a profoundly meaningful, soul-level connection.",
    8: "Combined, your energy radiates material ambition and the desire for achievement. This is a powerhouse partnership built for success.",
    9: "Your relationship carries a humanitarian, compassionate energy. Together you are drawn to serve, inspire, and make a meaningful difference in the world.",
}

GIFT_QUALITIES = {
    1: "Confidence & self-expression",
    2: "Intuition & emotional sensitivity",
    3: "Creativity & imagination",
    4: "Practicality & discipline",
    5: "Adaptability & freedom",
    6: "Love & responsibility",
    7: "Spirituality & inner wisdom",
    8: "Ambition & material strength",
    9: "Compassion & humanitarianism",
}

PLANE_COMPAT_TEXT = {
    ("Action Plane",   "Action Plane"):    "Double action energy — busy, productive and hands-on. Must ensure they make time to connect emotionally.",
    ("Action Plane",   "Practical Plane"): "Two action-oriented people — highly productive and efficient together. Great for shared goals and projects.",
    ("Action Plane",   "Soul Plane"):      "Action meets feeling — one brings momentum while the other brings warmth. A dynamic and caring relationship.",
    ("Action Plane",   "Spiritual Plane"): "Doing meets being — the practical one helps manifest the spiritual one's visions into reality.",
    ("Action Plane",   "Thought Plane"):   "Ideas meet action — one brings the vision while the other makes it real. A naturally productive combination.",
    ("Action Plane",   "Will Plane"):      "Determination meets action — a driven, goal-oriented combination that rarely fails to achieve its ambitions.",
    ("Practical Plane","Practical Plane"): "Both grounded and real-world focused — a stable, reliable, and materially secure relationship.",
    ("Practical Plane","Soul Plane"):      "Emotion meets pragmatism — heart and hands work together in a mutually supportive bond.",
    ("Practical Plane","Spiritual Plane"): "Vision meets groundedness — the spiritual one elevates while the practical one ensures stability.",
    ("Practical Plane","Thought Plane"):   "Thinking meets doing — a balanced pair where ideas are always grounded in practicality.",
    ("Practical Plane","Will Plane"):      "Drive meets practicality — a reliable, hard-working pair who gets things done without losing sight of real-world needs.",
    ("Soul Plane",     "Soul Plane"):      "Two deeply feeling souls — an empathic, emotionally rich relationship that must guard against mutual over-sensitivity.",
    ("Soul Plane",     "Spiritual Plane"): "Spirit meets soul — an intensely meaningful and karmic bond. You feel you have known each other before.",
    ("Soul Plane",     "Thought Plane"):   "Logic meets emotion — one grounds the feelings of the other while gaining depth in return.",
    ("Soul Plane",     "Will Plane"):      "Willpower meets emotional depth — one provides the drive, the other the heart. A deeply fulfilling bond.",
    ("Spiritual Plane","Spiritual Plane"): "A deeply soulful connection — shared spiritual values, introspection, and a sense of higher purpose.",
    ("Spiritual Plane","Thought Plane"):   "Intellect and spirit interweave — deep philosophical discussions and mutual growth characterize this bond.",
    ("Spiritual Plane","Will Plane"):      "Inner drive meets inner wisdom — a transformative combination that can inspire and lead others.",
    ("Thought Plane",  "Thought Plane"):   "Both lead with the mind — intellectual conversations, shared curiosity, and deep analysis define this relationship.",
    ("Thought Plane",  "Will Plane"):      "Mind meets willpower — the thinker and the doer complement each other beautifully, balancing strategy with execution.",
    ("Will Plane",     "Will Plane"):      "Two strong wills — powerful and unstoppable when aligned, but requires compromise to avoid power struggles.",
}

def get_compat_score(a, b):
    return COMPAT_MATRIX.get((min(a, b), max(a, b)), 5)

def _sk(n):
    if n in (11, 22, 33):
        return n % 9 or 9
    return n

# ── Helper ─────────────────────────────────────────────────────────────────────

def build_report(name, dob_str):
    """Parse DOB and run all calculations, returning enriched report dict."""
    parts = dob_str.split('-')
    if len(parts[0]) == 4:  # YYYY-MM-DD format from HTML date input
        year, month, day = (int(x) for x in parts)
    else:  # DD-MM-YYYY format
        day, month, year = (int(x) for x in parts)
    data = calculate_all(name, day, month, year)

    mulank = data['mulank']
    bhagyank = data['bhagyank']

    # Clamp master numbers to 9 for dict lookups
    def safe_key(n):
        if n in (11, 22, 33):
            return n % 9 or 9
        return n

    mk = safe_key(mulank)
    bk = safe_key(bhagyank)

    py = data['personal_year']
    pyk = safe_key(py)

    conn = data['connection']
    connk = safe_key(conn)

    pers = data['personality']
    persk = safe_key(pers)

    su = data['soul_urge']
    suk = safe_key(su)

    suc = data['success']
    suck = safe_key(suc)

    mat = data['maturity']
    matk = safe_key(mat)

    grid = data['grid']
    missing = data['missing']
    first_letter = data['first_letter']

    # Build Lo Shu interpretations for present numbers
    loshu_interps = {}
    for digit, count in grid.items():
        if count > 0:
            capped = min(count, 3)
            loshu_interps[digit] = LOSHU_INTERPRETATIONS[digit][capped]

    # Personal year luck for this mulank
    py_data = PERSONAL_YEAR_DATA[pyk]
    luck_key = f"M{mk}"
    luck_pct = py_data['luck'].get(luck_key, 70)

    # Career
    career_key = (mk, bk)
    career = CAREER_DATA.get(career_key, {
        "general": f"Mulank {mulank} and Bhagyank {bhagyank} combine leadership with purpose.",
        "fields": "Business, Consulting, Management, Service Industries",
        "strengths": "determination, adaptability, purpose-driven work",
        "challenges": "balance between personal goals and service"
    })

    # ── Pinnacles & Challenges ───────────────────────────────────────────────
    today = date.today()
    current_age = today.year - year - (1 if (today.month, today.day) < (month, day) else 0)

    pinnacle_nums = get_pinnacles(day, month, year)
    p1_end = 36 - bk  # bk is already the single-digit safe key of bhagyank
    pinnacle_ranges = [
        (0,       p1_end),
        (p1_end,  p1_end + 9),
        (p1_end + 9,  p1_end + 18),
        (p1_end + 18, None),
    ]
    active_pin_idx = next(
        (i for i, (s, e) in enumerate(pinnacle_ranges) if e is None or current_age < e),
        3
    )
    pinnacle_list = []
    for i, (num, (s, e)) in enumerate(zip(pinnacle_nums, pinnacle_ranges)):
        pinnacle_list.append({
            'number': i + 1,
            'pinnacle': num,
            'age_range': f"{s}–{e - 1}" if e else f"{s}+",
            'is_active': i == active_pin_idx,
            'data': PINNACLE_DATA[num],
        })

    challenge_nums = get_challenges(day, month, year)
    challenge_labels = ['First Challenge', 'Second Challenge', 'Main Challenge', 'Fourth Challenge']
    challenge_list = []
    for i, num in enumerate(challenge_nums):
        is_main = (i == 2)
        is_period = (i == active_pin_idx) or (i == 3 and active_pin_idx >= 2)
        challenge_list.append({
            'number': i + 1,
            'challenge': num,
            'label': challenge_labels[i],
            'is_main': is_main,
            'is_active': is_main or is_period,
            'data': CHALLENGE_DATA[num],
        })

    # ── Personal Month & Day ─────────────────────────────────────────────────
    personal_month = get_personal_month(py, today.month)
    personal_day = get_personal_day(personal_month, today.day)

    days_in_month = calendar.monthrange(today.year, today.month)[1]
    daily_forecast = [
        {
            'day': d,
            'personal_day': get_personal_day(personal_month, d),
            'pd_data': PERSONAL_DAY_DATA[get_personal_day(personal_month, d)],
        }
        for d in range(1, days_in_month + 1)
    ]

    MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_forecast = [
        {
            'month_num': m,
            'month_name': MONTH_NAMES[m - 1],
            'personal_month': get_personal_month(py, m),
            'pm_data': PERSONAL_MONTH_DATA[get_personal_month(py, m)],
        }
        for m in range(1, 13)
    ]

    # ── Lo Shu Arrows ────────────────────────────────────────────────────────
    strength_arrows = []
    isolation_arrows = []
    for arrow in LOSHU_ARROWS:
        nums = arrow['numbers']
        all_present = all(grid[n] > 0 for n in nums)
        all_absent = all(grid[n] == 0 for n in nums)
        if all_present:
            strength_arrows.append({'name': arrow['name'], 'numbers': nums, 'text': arrow['strength']})
        elif all_absent:
            isolation_arrows.append({'name': arrow['name'], 'numbers': nums, 'text': arrow['isolation']})

    # ── Lo Shu Planes ────────────────────────────────────────────────────────
    planes_analysis = []
    for plane in LOSHU_PLANES:
        nums = plane['numbers']
        present = [n for n in nums if grid[n] > 0]
        absent = [n for n in nums if grid[n] == 0]
        count = len(present)
        planes_analysis.append({
            'name': plane['name'],
            'numbers': nums,
            'present': present,
            'absent': absent,
            'count': count,
            'status': 'strong' if count == 3 else 'partial' if count > 0 else 'absent',
            'description': plane['description'],
        })

    # ── Lo Shu Special Combos ────────────────────────────────────────────────
    detected_combos = [
        {'label': combo['label'], 'text': combo['text']}
        for combo in LOSHU_SPECIAL_COMBOS
        if all(grid.get(n, 0) >= cnt for n, cnt in combo['condition'].items())
    ]

    report = {
        **data,
        'mulank_data': MULANK_DATA[mk],
        'bhagyank_text': BHAGYANK_DATA[bk],
        'love_sex_text': LOVE_SEX_DATA[bk],
        'connection_text': CONNECTION_DATA[connk],
        'personality_text': PERSONALITY_DATA[persk],
        'soul_urge_text': SOUL_URGE_DATA[suk],
        'first_letter_text': FIRST_LETTER_DATA.get(first_letter, "A unique individual with special gifts and qualities all your own."),
        'success_data': SUCCESS_DATA[suck],
        'maturity_text': MATURITY_DATA[matk],
        'personal_year_data': py_data,
        'personal_year_luck': luck_pct,
        'career': career,
        'loshu_interps': loshu_interps,
        'missing_data': {n: MISSING_NUMBER_DATA[n] for n in missing if n in MISSING_NUMBER_DATA},
        'personal_month': personal_month,
        'personal_month_data': PERSONAL_MONTH_DATA[personal_month],
        'personal_day': personal_day,
        'personal_day_data': PERSONAL_DAY_DATA[personal_day],
        'monthly_forecast': monthly_forecast,
        'today_str': today.strftime('%d %B %Y'),
        'current_month': today.month,
        'today_day': today.day,
        'daily_forecast': daily_forecast,
        'strength_arrows': strength_arrows,
        'isolation_arrows': isolation_arrows,
        'planes_analysis': planes_analysis,
        'detected_combos': detected_combos,
        'current_age': current_age,
        'pinnacle_list': pinnacle_list,
        'challenge_list': challenge_list,
    }
    return report


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate-report', methods=['POST'])
def generate_report():
    body = request.get_json()
    name = body.get('name', '').strip()
    dob = body.get('dob', '').strip()
    if not name or not dob:
        return jsonify({'error': 'Name and date of birth are required'}), 400
    try:
        report = build_report(name, dob)
        # Convert grid keys to strings for JSON
        report['grid'] = {str(k): v for k, v in report['grid'].items()}
        report['loshu_rows'] = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
        # Convert loshu_interps keys to strings
        report['loshu_interps'] = {str(k): v for k, v in report['loshu_interps'].items()}
        # Convert missing_data keys to strings
        report['missing_data'] = {str(k): v for k, v in report['missing_data'].items()}
        return jsonify(report)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    body = request.get_json()
    name = body.get('name', '').strip()
    dob = body.get('dob', '').strip()
    report_id = body.get('report_id')
    storage_only = body.get('storage_only', False)
    if not name or not dob:
        return jsonify({'error': 'Name and date of birth are required'}), 400

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        report = build_report(name, dob)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=20 * mm, leftMargin=20 * mm,
                                topMargin=20 * mm, bottomMargin=20 * mm)

        styles = getSampleStyleSheet()
        gold = colors.HexColor('#f5a623')
        dark_brown = colors.HexColor('#8B4513')
        cream = colors.HexColor('#FFF8F0')

        title_style = ParagraphStyle('Title', parent=styles['Title'],
                                     textColor=dark_brown, fontSize=24, spaceAfter=6,
                                     alignment=TA_CENTER)
        h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
                                  textColor=dark_brown, fontSize=14, spaceAfter=4,
                                  spaceBefore=12)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                                  textColor=colors.HexColor('#D4A017'), fontSize=12,
                                  spaceAfter=3, spaceBefore=8)
        body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                    fontSize=10, spaceAfter=6, leading=15)

        story = []

        # Title
        story.append(Paragraph("Numerology Report", title_style))
        story.append(Paragraph(
            f"<b>{report['name']}</b> — DOB: {report['dob']}",
            ParagraphStyle('sub', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, spaceAfter=4)
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=gold))
        story.append(Spacer(1, 6 * mm))

        # Numbers summary table
        nums = [
            ['Mulank', str(report['mulank']), 'Bhagyank', str(report['bhagyank'])],
            ['Connection', str(report['connection']), 'Personality', str(report['personality'])],
            ['Soul Urge', str(report['soul_urge']), 'Success', str(report['success'])],
            ['Maturity', str(report['maturity']), 'Personal Year', str(report['personal_year'])],
        ]
        t = Table(nums, colWidths=[45 * mm, 25 * mm, 45 * mm, 25 * mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cream),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_brown),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, gold),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [cream, colors.HexColor('#FFF0D8')]),
            ('FONTSIZE', (1, 0), (1, -1), 12),
            ('FONTSIZE', (3, 0), (3, -1), 12),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ]))
        story.append(t)
        story.append(Spacer(1, 6 * mm))

        def section(title, content_paragraphs):
            story.append(HRFlowable(width="100%", thickness=1, color=gold))
            story.append(Paragraph(title, h1_style))
            for p in content_paragraphs:
                if p:
                    story.append(Paragraph(str(p), body_style))

        # 1. Mulank
        def _sk_pdf(n):
            if n in (11, 22, 33): return n % 9 or 9
            return n
        mk = _sk_pdf(report['mulank'])
        bk = _sk_pdf(report['bhagyank'])
        def format_mulank_para(p):
            for label in ['Favourable Period:', 'Unfavourable Period:', 'Lucky Colours:']:
                if p.startswith(label):
                    rest = p[len(label):].strip()
                    return f'<font size="12"><b>{label}</b></font> {rest}'
            return p
        mulank_pdf_paras = [format_mulank_para(p) for p in MULANK_PDF_DATA[mk].split('\n') if p.strip()]
        section(f"1. {report['mulank_data']['title']}", mulank_pdf_paras)

        # 2. Bhagyank
        bhagyank_pdf_paras = [p for p in BHAGYANK_PDF_DATA[bk].split('\n') if p.strip()]
        section(f"2. Bhagyank {report['bhagyank']} — Destiny Number", bhagyank_pdf_paras)

        # 3. Love & Sex
        love_sex_pdf_paras = [p for p in LOVE_SEX_PDF_DATA[bk].split('\n') if p.strip()]
        section("3. Love & Sex Style", love_sex_pdf_paras)

        # 4. Connection Number
        section(f"4. Connection Number: {report['connection']}", [
            report['connection_text'],
        ])

        # 5. Personality Number
        section(f"5. Personality Number: {report['personality']}", [
            report['personality_text'],
        ])

        # 6. Soul Urge Number
        su_lines = report['soul_urge_text'].split('.')
        section(f"6. Soul Urge Number: {report['soul_urge']}", [
            report['soul_urge_text'],
        ])

        # 7. First Letter
        section(f"7. First Letter of Name: {report['first_letter']}", [
            report['first_letter_text'],
        ])

        # 8. Success Number
        sd = report['success_data']
        section(f"8. Success Number: {report['success']}", [
            f"<font size=\"11\"><b>Qualities</b></font>",
            sd['qualities'],
            f"<font size=\"11\"><b>Challenges</b></font>",
            sd['challenges'],
        ])

        # 9. Maturity Number
        section(f"9. Maturity Number: {report['maturity']}", [
            report['maturity_text'],
        ])

        # 10. Personal Year
        pyd = report['personal_year_data']
        section(f"10. Personal Year {report['personal_year']} ({report['current_year']})", [
            f"<font size=\"11\"><b>{pyd['title']}</b></font>",
            f"<font size=\"11\"><b>Positive Results</b></font>",
            pyd['positive'],
            f"<font size=\"11\"><b>Negative Results</b></font>",
            pyd['negative'],
            f"<font size=\"11\"><b>Your Luck This Year: {report['personal_year_luck']}%</b></font>",
        ])

        # 11. Personal Month
        pmd = report['personal_month_data']
        section(f"11. Personal Month {report['personal_month']} — {report['today_str']}", [
            f"<font size=\"11\"><b>Positive Traits This Month</b></font>",
            pmd['positive'],
            f"<font size=\"11\"><b>Watch Out For</b></font>",
            pmd['negative'],
            f"<font size=\"11\"><b>Tips for This Month</b></font>",
            pmd['tips'],
        ])

        # Monthly Forecast table
        forecast = report['monthly_forecast']
        cur_month = report['current_month']
        MONTH_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        fc_data = [['Month', 'PM'], ['Month', 'PM'], ['Month', 'PM'], ['Month', 'PM']]
        fc_rows = [fc['month_name'][:3] + ' — PM ' + str(fc['personal_month']) for fc in forecast]
        fc_table_data = [fc_rows[i:i+2] for i in range(0, 12, 2)]
        ft = Table(fc_table_data, colWidths=[75 * mm, 75 * mm])
        ft.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cream),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_brown),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, gold),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [cream, colors.HexColor('#FFF0D8')]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        for row_i, fc_row in enumerate(fc_table_data):
            for col_i, cell_text in enumerate(fc_row):
                month_idx = row_i * 2 + col_i
                if forecast[month_idx]['month_num'] == cur_month:
                    ft.setStyle(TableStyle([
                        ('BACKGROUND', (col_i, row_i), (col_i, row_i), gold),
                        ('FONTNAME', (col_i, row_i), (col_i, row_i), 'Helvetica-Bold'),
                    ]))
        story.append(ft)
        story.append(Spacer(1, 4 * mm))

        # 12. Personal Day
        pdd = report['personal_day_data']
        section(f"12. Personal Day {report['personal_day']} — {report['today_str']}", [
            pdd['text'],
            f"<font size=\"11\"><b>Social Style</b></font>",
            pdd['social_hints'],
            f"<font size=\"11\"><b>Lucky Colours Today</b></font>",
            pdd['lucky_colors'],
        ])

        # 13. Career
        car = report['career']
        section(f"13. Career Numerology (Mulank {report['mulank']} + Bhagyank {report['bhagyank']})", [
            car['general'],
            f"<font size=\"11\"><b>Recommended Career Fields</b></font>",
            car['fields'],
            f"<font size=\"11\"><b>Key Strengths</b></font>",
            car['strengths'],
            f"<font size=\"11\"><b>Challenges to Overcome</b></font>",
            car['challenges'],
        ])

        # 14. Lo Shu Grid
        story.append(HRFlowable(width="100%", thickness=1, color=gold))
        story.append(Paragraph("14. Lo Shu Grid", h1_style))

        grid = report['grid']
        loshu_rows = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
        grid_data = []
        for row in loshu_rows:
            grid_row = []
            for num in row:
                count = grid.get(str(num), grid.get(num, 0))
                if count > 0:
                    grid_row.append(' '.join([str(num)] * count))
                else:
                    grid_row.append(f"{num}")
            grid_data.append(grid_row)

        gt = Table(grid_data, colWidths=[30 * mm, 30 * mm, 30 * mm])
        gt_style = [
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1.5, gold),
            ('ROWHEIGHT', (0, 0), (-1, -1), 30 * mm),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]

        for r_idx, row in enumerate(loshu_rows):
            for c_idx, num in enumerate(row):
                count = grid.get(str(num), grid.get(num, 0))
                if count > 0:
                    gt_style.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), gold))
                    gt_style.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.black))
                else:
                    gt_style.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#e0e0e0')))
                    gt_style.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.grey))

        gt.setStyle(TableStyle(gt_style))
        story.append(gt)
        story.append(Spacer(1, 4 * mm))

        # Lo Shu interpretations
        for digit, interp in sorted(report['loshu_interps'].items()):
            story.append(Paragraph(f"<b>Number {digit}:</b> {interp}", body_style))

        # Planes
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph("<b>Planes Analysis</b>", h2_style))
        for plane in report['planes_analysis']:
            status_label = {'strong': 'Complete', 'partial': 'Partial', 'absent': 'Absent'}.get(plane['status'], '')
            nums_str = ', '.join(str(n) for n in plane['numbers'])
            story.append(Paragraph(
                f"<b>{plane['name']}</b> ({nums_str}) — <i>{status_label}</i>: {plane['description']}",
                body_style
            ))

        # Arrows of Strength
        if report['strength_arrows']:
            story.append(Spacer(1, 3 * mm))
            story.append(Paragraph("<b>Arrows of Strength</b>", h2_style))
            for arrow in report['strength_arrows']:
                nums_str = '-'.join(str(n) for n in arrow['numbers'])
                story.append(Paragraph(f"<b>{arrow['name']}</b> ({nums_str}): {arrow['text']}", body_style))

        # Arrows of Isolation
        if report['isolation_arrows']:
            story.append(Spacer(1, 3 * mm))
            story.append(Paragraph("<b>Arrows of Isolation</b>", h2_style))
            for arrow in report['isolation_arrows']:
                nums_str = '-'.join(str(n) for n in arrow['numbers'])
                story.append(Paragraph(f"<b>{arrow['name']}</b> ({nums_str}): {arrow['text']}", body_style))

        # Special Combinations
        if report['detected_combos']:
            story.append(Spacer(1, 3 * mm))
            story.append(Paragraph("<b>Special Combinations in Your Grid</b>", h2_style))
            for combo in report['detected_combos']:
                story.append(Paragraph(f"<b>{combo['label']}:</b> {combo['text']}", body_style))

        # 15. Missing Numbers
        story.append(HRFlowable(width="100%", thickness=1, color=gold))
        story.append(Paragraph("15. Missing Numbers — Impact & Remedy", h1_style))

        if report['missing']:
            for num in report['missing']:
                mn = MISSING_NUMBER_DATA.get(num)
                if mn:
                    story.append(Paragraph(f"<b>Missing Number {num}:</b>", h2_style))
                    story.append(Paragraph(f"<b>Impact:</b> {mn['impact']}", body_style))
                    story.append(Paragraph(f"<b>Remedy ({mn['remedy_day']}):</b> {mn['remedy']}", body_style))
        else:
            story.append(Paragraph(
                "All numbers 1-9 are present in your date of birth. You are blessed with a complete Lo Shu Grid!",
                body_style))

        # Consultation section
        story.append(Spacer(1, 10 * mm))
        story.append(HRFlowable(width="100%", thickness=2, color=gold))
        story.append(Spacer(1, 6 * mm))
        consult_heading = ParagraphStyle('ConsultHeading', parent=styles['Normal'],
                                         alignment=TA_CENTER, fontSize=9, textColor=gold,
                                         spaceAfter=4, fontName='Helvetica-Bold',
                                         letterSpacing=1)
        consult_name = ParagraphStyle('ConsultName', parent=styles['Normal'],
                                      alignment=TA_CENTER, fontSize=16, textColor=dark_brown,
                                      spaceAfter=2, fontName='Helvetica-Bold')
        consult_body = ParagraphStyle('ConsultBody', parent=styles['Normal'],
                                      alignment=TA_CENTER, fontSize=10, textColor=colors.HexColor('#5a3a1a'),
                                      spaceAfter=6, leading=15)
        story.append(Paragraph("NAME CORRECTION &amp; PERSONAL CONSULTATION", consult_heading))
        story.append(Paragraph("Madhu Prasad", consult_name))
        story.append(Paragraph("Certified Numerologist", consult_body))
        story.append(Paragraph(
            "Is your name aligned with your numbers? A personalised name correction can bring "
            "harmony between your name’s vibration and your birth numbers.",
            consult_body))
        story.append(Paragraph(
            "<b>WhatsApp / Call:</b> +91 91633 62273",
            ParagraphStyle('ConsultContact', parent=styles['Normal'],
                           alignment=TA_CENTER, fontSize=11, textColor=dark_brown,
                           fontName='Helvetica-Bold', spaceAfter=4)))
        story.append(Spacer(1, 6 * mm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0c080')))
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(
            "Report generated with Numerology Report App",
            ParagraphStyle('footer', parent=styles['Normal'],
                           alignment=TA_CENTER, textColor=colors.grey, fontSize=9)
        ))

        doc.build(story)
        pdf_bytes = buffer.getvalue()

        # Upload to Supabase Storage and update record
        pdf_url = None
        if db and report_id:
            try:
                import re
                from datetime import datetime as _dt
                safe = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
                file_path = f"{safe}_{dob.replace('/', '-')}_{_dt.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
                db.storage.from_('reports').upload(
                    path=file_path,
                    file=pdf_bytes,
                    file_options={'contentType': 'application/pdf', 'upsert': 'true'}
                )
                pdf_url = db.storage.from_('reports').get_public_url(file_path)
                db.table('reports').update({'pdf_url': pdf_url}).eq('id', report_id).execute()
                print(f'[PDF] Uploaded: {file_path} → {pdf_url}')
            except Exception as e:
                import traceback
                print(f'[PDF] Storage upload failed: {e}')
                traceback.print_exc()

        if storage_only:
            return jsonify({'ok': True, 'pdf_url': pdf_url})

        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{name} - Numerology Report.pdf"'
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/check-compatibility', methods=['POST'])
def check_compatibility():
    body = request.get_json()
    name1 = body.get('name1', '').strip()
    dob1  = body.get('dob1', '').strip()
    name2 = body.get('name2', '').strip()
    dob2  = body.get('dob2', '').strip()

    if not all([name1, dob1, name2, dob2]):
        return jsonify({'error': 'All four fields are required.'}), 400

    def parse_dob(s):
        parts = s.split('-')
        if len(parts[0]) == 4:
            yr, mo, dy = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            dy, mo, yr = int(parts[0]), int(parts[1]), int(parts[2])
        return dy, mo, yr

    try:
        d1, m1, y1 = parse_dob(dob1)
        d2, m2, y2 = parse_dob(dob2)
    except Exception:
        return jsonify({'error': 'Invalid date format.'}), 400

    try:
        from numerology import reduce_number as _rn
        r1 = calculate_all(name1, d1, m1, y1)
        r2 = calculate_all(name2, d2, m2, y2)

        mk1, mk2 = _sk(r1['mulank']),    _sk(r2['mulank'])
        bk1, bk2 = _sk(r1['bhagyank']),  _sk(r2['bhagyank'])
        nn1, nn2 = _sk(r1['name_number']), _sk(r2['name_number'])

        ms = get_compat_score(mk1, mk2)
        bs = get_compat_score(bk1, bk2)
        ns = get_compat_score(nn1, nn2)

        overall_9 = ms * 0.40 + bs * 0.35 + ns * 0.25
        overall_pct = round(overall_9 / 9 * 100)

        rel_num = _rn(mk1 + mk2, keep_master=False)

        planet_names = {1:'Sun',2:'Moon',3:'Jupiter',4:'Rahu',5:'Mercury',
                        6:'Venus',7:'Ketu',8:'Saturn',9:'Mars'}

        # ── Lo Shu Grid Compatibility ──────────────────────────────────────────
        grid1 = r1['grid']   # {1-9: count}, integer keys
        grid2 = r2['grid']
        combined = {n: grid1[n] + grid2[n] for n in range(1, 10)}

        gifts_1_to_2  = [n for n in range(1, 10) if grid1[n] > 0 and grid2[n] == 0]
        gifts_2_to_1  = [n for n in range(1, 10) if grid2[n] > 0 and grid1[n] == 0]
        shared_present = [n for n in range(1, 10) if grid1[n] > 0 and grid2[n] > 0]
        shared_missing  = [n for n in range(1, 10) if grid1[n] == 0 and grid2[n] == 0]

        p2_missing = [n for n in range(1, 10) if grid2[n] == 0]
        p1_missing = [n for n in range(1, 10) if grid1[n] == 0]
        comp_p1_pct = round(len(gifts_1_to_2) / max(len(p2_missing), 1) * 100) if p2_missing else 100
        comp_p2_pct = round(len(gifts_2_to_1) / max(len(p1_missing), 1) * 100) if p1_missing else 100
        overall_comp_pct = round((comp_p1_pct + comp_p2_pct) / 2)

        def get_dp(grid):
            best = None; best_count = -1
            for plane in LOSHU_PLANES:
                c = sum(1 for n in plane['numbers'] if grid[n] > 0)
                if c > best_count: best_count = c; best = plane['name']
            return best

        dp1_name = get_dp(grid1)
        dp2_name = get_dp(grid2)
        p_key = tuple(sorted([dp1_name, dp2_name]))
        plane_compat_text = PLANE_COMPAT_TEXT.get(
            p_key, "A unique energy combination with its own special dynamic."
        )

        overloaded = [n for n in range(1, 10) if combined[n] >= 3]
        combined_unique = sum(1 for n in range(1, 10) if combined[n] > 0)

        def arr_present(nums, g): return all(g[n] > 0 for n in nums)
        arr_new, arr_sustained, arr_absent = [], [], []
        for arr in LOSHU_ARROWS:
            has1 = arr_present(arr['numbers'], grid1)
            has2 = arr_present(arr['numbers'], grid2)
            hasc = arr_present(arr['numbers'], combined)
            if hasc:
                (arr_new if not has1 and not has2 else arr_sustained).append(arr['name'])
            else:
                arr_absent.append(arr['name'])

        sr = {'absent': 0, 'partial': 1, 'complete': 2}
        def ps(nums, g):
            c = sum(1 for n in nums if g[n] > 0)
            return 'absent' if c == 0 else ('complete' if c == len(nums) else 'partial')

        planes_compat = []
        for plane in LOSHU_PLANES:
            s1 = ps(plane['numbers'], grid1)
            s2 = ps(plane['numbers'], grid2)
            sc = ps(plane['numbers'], combined)
            bi = max(s1, s2, key=lambda s: sr[s])
            planes_compat.append({
                'name': plane['name'],
                'state_p1': s1, 'state_p2': s2, 'state_combined': sc,
                'upgraded': sr[sc] > sr[bi],
            })

        key_nums = {
            str(n): {'planet': pl, 'theme': th,
                     'p1': grid1[n], 'p2': grid2[n], 'combined': combined[n]}
            for n, pl, th in [
                (2, 'Moon', 'Emotional Bond'),
                (6, 'Venus', 'Love & Harmony'),
                (9, 'Mars', 'Passion'),
            ]
        }

        return jsonify({
            'person1': {
                'name': name1, 'dob': r1['dob'],
                'mulank': r1['mulank'], 'mulank_key': mk1, 'mulank_planet': planet_names[mk1],
                'bhagyank': r1['bhagyank'], 'bhagyank_key': bk1, 'bhagyank_planet': planet_names[bk1],
                'name_number': r1['name_number'], 'nn_key': nn1,
            },
            'person2': {
                'name': name2, 'dob': r2['dob'],
                'mulank': r2['mulank'], 'mulank_key': mk2, 'mulank_planet': planet_names[mk2],
                'bhagyank': r2['bhagyank'], 'bhagyank_key': bk2, 'bhagyank_planet': planet_names[bk2],
                'name_number': r2['name_number'], 'nn_key': nn2,
            },
            'scores': {
                'mulank': ms,
                'bhagyank': bs,
                'name_number': ns,
                'overall_pct': overall_pct,
            },
            'relationship_number': rel_num,
            'relationship_text': RELATIONSHIP_NUMBER_DATA[rel_num],
            'pair_text': COMPAT_PAIR_TEXT.get(
                (min(mk1, mk2), max(mk1, mk2)),
                'A unique combination with its own special chemistry.'
            ),
            'loshu_compat': {
                'grid1': {str(k): v for k, v in grid1.items()},
                'grid2': {str(k): v for k, v in grid2.items()},
                'combined': {str(k): v for k, v in combined.items()},
                'gifts_1_to_2': gifts_1_to_2,
                'gifts_2_to_1': gifts_2_to_1,
                'shared_present': shared_present,
                'shared_missing': shared_missing,
                'comp_p1_pct': comp_p1_pct,
                'comp_p2_pct': comp_p2_pct,
                'overall_comp_pct': overall_comp_pct,
                'dominant_plane_1': dp1_name,
                'dominant_plane_2': dp2_name,
                'plane_compat_text': plane_compat_text,
                'overloaded': overloaded,
                'combined_unique': combined_unique,
                'arrows_new': arr_new,
                'arrows_sustained': arr_sustained,
                'arrows_absent': arr_absent,
                'planes': planes_compat,
                'key_nums': key_nums,
                'gift_qualities': {str(k): v for k, v in GIFT_QUALITIES.items()},
            },
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ── Save Client ────────────────────────────────────────────────────────────────

@app.route('/save-client', methods=['POST'])
def save_client():
    if not db:
        return jsonify({'error': 'Database not configured'}), 500
    body = request.get_json()
    name     = body.get('name', '').strip()
    dob      = body.get('dob', '').strip()
    phone    = body.get('phone', '').strip()
    email    = body.get('email', '').strip()
    notes    = body.get('notes', '').strip()
    summary  = body.get('summary')          # key numbers only

    if not name or not dob:
        return jsonify({'error': 'Name and DOB are required'}), 400
    try:
        res = db.table('clients').insert({
            'name': name, 'dob': dob,
            'phone': phone or None,
            'email': email or None,
            'notes': notes or None,
        }).execute()
        client_id = res.data[0]['id']
        report_id = None
        if summary:
            r = db.table('reports').insert({
                'client_id': client_id,
                'report_data': summary,
            }).execute()
            report_id = r.data[0]['id']
        return jsonify({'success': True, 'client_id': client_id, 'report_id': report_id})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/save-compatibility', methods=['POST'])
def save_compatibility_report():
    if not db:
        return jsonify({'error': 'Database not configured'}), 500
    body = request.get_json()
    name         = body.get('name', '').strip()
    dob          = body.get('dob', '').strip()
    phone        = body.get('phone', '').strip()
    email        = body.get('email', '').strip()
    partner_name = body.get('partner_name', '').strip()
    partner_dob  = body.get('partner_dob', '').strip()
    overall_pct  = body.get('overall_pct')
    compat_data  = body.get('compat_data')

    if not name or not dob or not partner_name or not partner_dob:
        return jsonify({'error': 'All fields required'}), 400
    try:
        res = db.table('clients').insert({
            'name': name, 'dob': dob,
            'phone': phone or None,
            'email': email or None,
        }).execute()
        client_id = res.data[0]['id']
        db.table('compatibility_reports').insert({
            'client_id': client_id,
            'partner_name': partner_name,
            'partner_dob': partner_dob,
            'overall_pct': overall_pct,
            'report_data': compat_data,
        }).execute()
        return jsonify({'success': True, 'client_id': client_id})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ── Admin ───────────────────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == os.environ.get('ADMIN_PASSWORD', ''):
            session['admin'] = True
            return redirect('/admin')
        error = 'Incorrect password. Please try again.'
    return render_template('admin_login.html', error=error)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')


@app.route('/admin')
@admin_required
def admin_dashboard():
    if not db:
        return 'Database not configured', 500
    q = request.args.get('q', '').strip()
    if q:
        clients = db.table('clients').select('*').ilike('name', f'%{q}%').order('created_at', desc=True).execute().data
    else:
        clients = db.table('clients').select('*').order('created_at', desc=True).execute().data

    total_reports = db.table('reports').select('id', count='exact').execute().count or 0
    total_compat  = db.table('compatibility_reports').select('id', count='exact').execute().count or 0

    return render_template('admin_dashboard.html',
                           clients=clients, q=q,
                           total_clients=len(clients),
                           total_reports=total_reports,
                           total_compat=total_compat)


@app.route('/admin/client/<client_id>')
@admin_required
def admin_client(client_id):
    if not db:
        return 'Database not configured', 500
    client       = db.table('clients').select('*').eq('id', client_id).single().execute().data
    reports      = db.table('reports').select('*').eq('client_id', client_id).order('generated_at', desc=True).execute().data
    compat       = db.table('compatibility_reports').select('*').eq('client_id', client_id).order('generated_at', desc=True).execute().data
    consultations= db.table('consultations').select('*').eq('client_id', client_id).order('date', desc=True).execute().data
    return render_template('admin_client.html',
                           client=client, reports=reports,
                           compat_reports=compat, consultations=consultations)


@app.route('/admin/client/<client_id>/add-consultation', methods=['POST'])
@admin_required
def add_consultation(client_id):
    if not db:
        return 'Database not configured', 500
    db.table('consultations').insert({
        'client_id': client_id,
        'date':  request.form.get('date') or None,
        'fee':   float(request.form.get('fee')) if request.form.get('fee') else None,
        'notes': request.form.get('notes') or None,
    }).execute()
    return redirect(f'/admin/client/{client_id}')


@app.route('/admin/pdf/<report_id>')
@admin_required
def download_report_pdf(report_id):
    if not db:
        return 'Database not configured', 500
    try:
        row = db.table('reports').select('pdf_url, client_id').eq('id', report_id).single().execute().data
        if not row or not row.get('pdf_url'):
            return 'PDF not found', 404
        client = db.table('clients').select('name').eq('id', row['client_id']).single().execute().data
        filename = f"{client['name']} - Numerology Report.pdf"
        import httpx as _httpx
        pdf_bytes = _httpx.get(row['pdf_url']).content
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        return str(e), 500


@app.route('/admin/client/<client_id>/delete', methods=['POST'])
@admin_required
def delete_client(client_id):
    if not db:
        return 'Database not configured', 500
    db.table('clients').delete().eq('id', client_id).execute()
    return redirect('/admin')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
