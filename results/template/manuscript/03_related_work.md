# American Pragmatism and the Public Criticism of Models {#sec:related_work}

American Pragmatism asks how inquiry earns and revises its commitments through consequences, criticism and shared experience. Its plural traditions supply distinct questions for this framework, rather than a historical derivation of the four roles or an anticipation of categorical active inference.

## Peirce: doubt, habit, and public correction

Peirce distinguishes scientific inquiry, answerable to an independent reality, from tenacity, authority and the a priori method [@peirce1877fixation]. These four methods concern the settlement of belief; they do not correspond to our four intersecting roles. His pragmatic maxim clarifies a conception through conceivable practical consequences [@peirce1878clear]; his later account connects belief, habit, surprise and self-control [@peirce1905pragmatism]. The modeling question is what a commitment leads us to expect and what could unsettle it. Posterior concentration alone supplies neither genuine doubt nor public correction: our misleading-metadata control shows internally coherent inference under inadequate premises.

## James: verification, consequences, and the correction of truth claims

James asks what difference competing ideas make in experience, while making verification, consistency and subsequent correction central to truth claims [@james1907pragmatism], Lectures II and VI. This directs attention to predicted observations, changed actions, incurred costs and possible counterevidence. It does not identify truth with convenience or one performance score. Accuracy and proper losses reveal different consequences; their selection and evaluation horizon remain contestable commitments.

## Dewey: reflective inquiry and the reconstruction of ends

For Dewey, reflection examines the grounds and consequences of belief and sustains inquiry through a problematic situation [@dewey1910think], Chapter I. A confidence-triggered observation rule captures only a narrow decision about continuing investigation. His treatment of ends through needs, opportunities and consequences also makes purposes available for reconstruction [@dewey1920reconstruction], Chapters VI--VII. Computing an action under $C$ therefore differs from asking whether $C$ expresses an adequate end. Our fixed evaluation criteria expose this distinction without implementing autonomous reconstruction of purposes.

## Addams: whose experience can correct the evaluator?

Addams challenges the sufficiency of private virtue for social ethics and brings diverse experience into the correction of moral judgment [@addams1902democracy], Introduction and Charitable Effort. Her question for evaluation is whose experience can contest the declared account of benefit and harm. A held-out test can assess a chosen outcome while excluding affected perspectives from its definition. Our synthetic contexts contain no social participants; participatory criticism is a normative requirement proposed for social applications, not a demonstrated software capability.

## Mead: significant symbols and meaning through shared conduct

Mead situates significant symbols in coordinated social conduct and the indication of anticipated consequences [@mead1934mind], Sections 16 and 24 of the posthumous volume edited by Charles W. Morris. A GNN label declares an intended meaning without establishing shared interpretation. Executable specifications can make disagreement about categories precise, but our single-agent tasks do not implement symbolic interaction or the social development of a self.

## What the pragmatist inheritance asks of an executable model

Together these readings ask us to articulate consequences, expose reasons, and permit criticism of representations and ends. The four roles cut across those responsibilities; no author belongs to one quadrant. In the demonstrations, the researcher specifies the world, model and evaluation. Public criticism and the social formation of ends remain outside the mechanism. A meta-pragmatic framework makes these choices inspectable without automating their justification or substituting philosophical authority for held-out evidence.

## Active inference, generative models, and explicit specification

The free energy principle and discrete active inference supply the background for the distinction between state inference and model specification [@friston2010free; @dacosta2020active]. Expected free energy balances information gain and outcome preferences under a predictive model [@friston2015epistemic]. The variational assumptions behind planning require care: expected free energy is not obtained by simply substituting future observations into the usual variational objective [@millidge2021whence]. Our implementation is deliberately limited to categorical models with known likelihood and transition matrices.

Methods and software already address learning, hierarchical models, and practical computation [@friston2016active; @smith2022step; @heins2022pymdp]. Thus, our meta-level interpretation does not introduce model learning to active inference. Its contribution is a classification of specification and monitoring choices, coupled to explicit examples that can be checked computationally.

Recent work studies scale-free generative models, variational planning, and interpretable graph-based agents [@friston2025scalefree; @devries2025planning; @feps2025]. These are distinct technical architectures, not implementations or validation of the quadrants proposed here. We include them to clarify the surrounding research program, without importing their performance claims into our results.

## OODA, active inference, and criticism across the action loop {#sec:ooda}

Boyd's observe--orient--decide--act (OODA) framework provides a useful comparison for inquiry organized around action. David, Cordes and Friedman explicitly connect OODA with active inference in *Active Inference in Modeling Conflict* [@david2021conflict], especially pp. 17--18 and 37--38, Figure 9. Their alignment relates observation to incoming signals, orientation to inference about hidden causes, decision to preference-sensitive policy evaluation, and action to an enacted policy. This is a conceptual antecedent, not empirical validation of our taxonomy or experiments.

The following crosswalk is our interpretation of the present executable tasks. It distinguishes a recurring action loop from responsibilities that can operate throughout it.

```{=latex}
\Needspace{12\baselineskip}
```

| OODA function | Connection to the present framework |
|---|---|
| Observe: receive evidence | Q1 updates from observations; Q3 controls whether further evidence is acquired. |
| Orient: interpret the situation | Q2 contextualizes evidence through source reliability; Q4 evaluates the assumed reliability model. |
| Decide: evaluate possible conduct | Q1 evaluates policies under declared preferences; Q3 exposes sensing costs and stopping criteria. |
| Act: intervene and encounter consequences | The action model's transition changes observation mode; external evaluation can then inform Q4 criticism. |

The shared count of four implies no one-to-one mapping. Repeatedly executing OODA under false source assumptions can preserve a bad orientation; the misleading-metadata and world--agent mismatch controls make narrower versions of this vulnerability inspectable. Our one-step action task executes a bounded perception--action coupling, not a strategic conflict simulation. The meta-pragmatic question cuts across the loop: what evidence, representation, purpose or resource judgment warrants revision, and who may authorize it?

## Metacognitive monitoring, control, and forecast calibration

The distinction between monitoring and control predates this taxonomy [@flavell1979metacognition; @nelson1990metamemory]. Confidence, calibration, discrimination, and metacognitive efficiency are different quantities [@fleming2014measure]. A concentrated posterior can be confidently wrong under model misspecification. Accordingly, the experiment reports Brier loss and log loss rather than treating posterior concentration as evidence of correctness.

MetaMind and SOFAI provide contemporary examples of metacognitive organization in artificial systems [@metamind2025; @sofai2025]. Their tasks and mechanisms differ from our binary sensor setting. An architectural analogy does not establish shared statistical behavior or biological equivalence.

## Outcome preferences, reward representations, and action selection

The difference between specifying outcome preferences and specifying rewards is useful, but it is not an absolute division between inspectable and opaque objectives. If preferences are encoded as $p_C(o)\propto\exp(\beta r(o))$, the expected log-preference term corresponds to expected reward up to a scale and normalization constant. Epistemic value adds a particular information-seeking objective. Active inference and model-based reinforcement learning have operational connections [@tschantz2019scaling; @sajid2021active]; both require assumptions about observations, actions, and values.

Our question is therefore comparative: which explicit reliability or monitoring mechanism changes behavior under a specified environment and resource budget? The four labels do not determine the answer in advance.

## AI safety, information integrity, and evidential vulnerability

Objective specification, distribution shift, and oversight are established concerns in AI safety [@amodei2016concrete; @gabriel2020artificial]. We use the quadrants to organize where an intervention acts: on observations, metadata, monitoring rules, or model revision. We do not infer human susceptibility, attack success probabilities, or alignment guarantees from the taxonomy. The misleading-metadata control is a controlled synthetic failure case, not a deployment security evaluation.

## Bayesian model criticism and the resource limits of inquiry

Gelman and Shalizi distinguish inference within a model from criticism and revision of the model itself [@gelman2013philosophy]. That distinction motivates our separation of posterior updating from the evaluation of its assumptions. Simon's bounded account of rational choice makes resource limitations relevant to a decision procedure [@simon1955behavioral]; accordingly, an accuracy improvement obtained with extra observations is evaluated alongside its cost.

Proper scoring rules provide a principled basis for assessing probabilistic forecasts [@gneiting2007scoring]. We use Brier and logarithmic losses in addition to classification accuracy. These losses assess forecast quality; neither is a pure calibration statistic. Descriptive calibration diagrams separately compare forecast probabilities with held-out frequencies, following the distinction between coherence and calibration [@dawid1982calibrated].

## Out-of-sample predictive assessment and the meanings of calibration

Bayesian workflow treats model construction, checking, computation, and comparison as linked activities rather than reducing scientific practice to a posterior calculation [@gelman2020workflow]. This supplies a methodological neighbor for the four roles: each role identifies a place where inquiry can change course, while workflow specifies how a sequence of such changes is evaluated. Our synthetic study implements one held-out evaluation cycle; it does not establish convergence of an open-ended revision process.

Predictive evaluation must follow the sampling structure. Demšar's comparisons concern algorithms across multiple datasets [@demsar2006comparisons]; our seed replicates are generated datasets within one environment, not independently chosen scientific domains. Thus, seed uncertainty cannot stand in for cross-domain generalization. Vehtari and colleagues analyze out-of-sample predictive evaluation with LOO and WAIC [@vehtari2017evaluation]. We use a separately generated test set and frozen fitted reliabilities; we do not claim to implement those estimators or their diagnostics.

The word calibration also needs an explicit object. Guo and colleagues examine confidence calibration in neural classifiers [@guo2017calibration], whereas our curves assess probabilities of state 1 in a binary generative task. Vaicenavicius and colleagues give a broader framework for evaluating probabilistic calibration [@vaicenavicius2019calibration]. Their distinctions motivate treating a binned reliability curve as a diagnostic with finite-sample and binning limitations. Simulation-based calibration instead checks an inference algorithm across generative draws [@talts2018calibration]. Our algebraic VFE/EFE identities and held-out forecast curves are different checks and should not be relabeled as simulation-based calibration.

## Resources and the scope of sensitivity analysis

Gigerenzer and Gaissmaier's ecological approach to heuristics makes strategy quality conditional on the structure of the decision environment [@gigerenzer2011heuristic]. This sharpens the interpretation of our stopping rule: a rule can economize on observations in this task without becoming a generally rational procedure. Our comparison does not establish which heuristics people use, nor does it estimate an ecological optimum.

Resource-rational analysis asks how computational constraints enter an account of cognitive performance [@lieder2020resource]. Our observation counts operationalize one resource; they do not measure cognitive effort, time, or energy. The comparison therefore supports a resource accounting argument while leaving the mapping to biological mechanisms unresolved.

Steegen and colleagues make analytical alternatives visible through multiverse analysis [@steegen2016multiverse]. Our threshold sweep follows that transparency motivation in a narrower setting: eleven explicit acquisition thresholds reuse the same test trials. It is a sensitivity analysis, not an exhaustive multiverse or an independent validation of a selected policy. Any threshold chosen from this sweep would need a new evaluation set.

## Situated inquiry and the origins of commitments

Dewey's treatment of the reflex arc emphasizes coordinated activity rather than an isolated stimulus followed by an isolated response [@dewey1896reflex]. This motivates asking how observation and action jointly define a task. Our action model implements one small, explicit coupling: an intervention changes the observation mode while preserving the hidden context. It does not reproduce Dewey's account of organismic coordination.

Friedman's *Before Pragmatism Had a Name* develops a reading of Blake alongside pragmatist inquiry and active inference [@friedman2026before]. We draw a bounded methodological lesson from this conceptual juxtaposition: an inherited representational habit can itself become an object of inquiry. The historical and literary synthesis is an attributed interpretation, not empirical support for the present taxonomy or a mathematical equivalence between Blake's figures and generative-model variables.

*Synthesis of Agent and Niche* stages a speculative encounter between Blake and ecological accounts of cognition [@friedman2025synthesis]. It directs attention toward the setting that makes an observation meaningful. Here that attention becomes a testable modeling distinction between a declared agent and a separately specified world. The literary work supplies conceptual context, whereas the retained executable specifications and scores supply evidence for the numerical comparison.

*Prior Cognitive Art* asks which explanatory question is being answered when the origin or persistence of a prior is invoked [@friedman2026prior]. Its conceptual organization draws on Tinbergen's questions about causation, development, survival value, and evolution [@tinbergen1963aims]. A fitted probability, a developmental account, and an evolutionary explanation are therefore different explanatory objects. Our fixed categorical prior is an input to a calculation. Neither a successful posterior update nor the addition of a hyperprior explains its biological origin. The cited working paper presents conceptual and deterministic illustrations, not stochastic performance evidence for our study.

## Research economy and public representations

Beni and Pietarinen connect active inference with Peirce's abduction, induction and economy of research [@beni2021aligning]. Their philosophical alignment is a close antecedent to the present interpretation. Our narrower contribution is to expose concrete commitments and their evaluation through retained executable models. Selecting an informative action within a fixed representation is not equivalent to inventing a representation; reducing prediction error alone does not authorize an unrestricted change of ends.

Diagrams also participate in scientific accountability. A visualization can make assumptions, units and comparisons inspectable, or conceal them through scale, typography and omission. Rougier and colleagues treat figure design as communication between data and readers [@rougier2014figures]. Here the conceptual quadrant map, exact model surfaces and seed-based estimates have different captions and visual roles. Readability does not turn a conceptual diagram into evidence, and numerical precision does not make a model adequate. A public representation should expose the distinction.

## Executable specification as an inspectable scientific artifact

The GNN project defines a structured notation and parsing pipeline for active-inference generative models [@gnn2026specification]. We import its reference Markdown parser at a recorded revision and consume the resulting parameter values. Our adapter admits a bounded, single-factor categorical profile. GNN is the specification dependency; the local exact categorical equations are the execution engine. No claim is made that every upstream backend, model family, or parser acceptance condition is supported by this adapter.
