## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
Stay-switch categorical agent

## ModelAnnotation
Two states, two outcomes, two actions. Action zero preserves the state; action one switches it.
A[outcome,state]; B[next,current,action]. Preferences are finite logits.

## StateSpaceBlock
A[2,2,type=float]
B[2,2,2,type=float]
C[2,type=float]
D[2,type=float]
s[2,type=float]
o[1,type=int]
u[1,type=int]

## Connections
D>s
s>A
A>o
s>B
u>B
B>s

## InitialParameterization
A=[[0.8,0.2],[0.2,0.8]]
B=[[[1.0,0.0],[0.0,1.0]],[[0.0,1.0],[1.0,0.0]]]
C=[1.0,-1.0]
D=[0.5,0.5]

## Equations
# q(s|o) is proportional to A[o,s] D[s].
# Normalized G = KL(q(o)||softmax(C)) + expected likelihood entropy.

## Time
Dynamic

## ActInfOntologyAnnotation
A=LikelihoodMatrix
B=TransitionMatrix
C=PreferenceVector
D=PriorBelief

## ModelParameters
num_hidden_states: 2
num_obs: 2
num_actions: 2

## Footer
Executable scientific profile: categorical-single-factor-v1.

## Signature
Author: Daniel Friedman research repository
