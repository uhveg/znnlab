clear;close all;clc;
% Implicit dynamics continuous-time zeroing neural network
A = @(t) [sin(t),cos(t);-cos(t),sin(t)];
VA = @(t, y)VectM(A(t));

X0 = rand(4,1)*2-1;

opt = odeset('Mass',VA);
[t, X] = ode45(@(t, x) dynamics(t, x), [0, 10], X0, opt);

iA = zeros(size(X));
frobNorm = zeros(size(t));
for i = 1:numel(t)
    iA(i, :) = reshape(A(t(i)), 4, 1);
    frobNorm(i) = norm(A(t(i)) * reshape(X(i,:), 2, 2)' - eye(2), 'fro');
end

figure;hold on;grid minor;
xlabel('time(s)', 'Interpreter', 'latex');
title('$\| A(t)X(t) - I \|_F$', 'Interpreter', 'latex');
plot(t, frobNorm);
axes('position',[.6 .19 .28 .25]);box on;
indexOfInterest = (t > 8);
plot(t(indexOfInterest), frobNorm(indexOfInterest));
figure('OuterPosition',[360,90,1200,900]);
for i=1:4
    subplot(2,2,i);hold on; grid minor;
    titleHandle = title(sprintf('$x_{%d,%d}$',ceil(i/2),2-mod(i,2)), 'Interpreter', 'latex');
    set(titleHandle, 'Units', 'normalized', 'Position', [0.5, 0.85, 0]);
    ylim([-2,2]);
    plot(t, iA(:,i), 'r');
    plot(t, X(:,i), 'b--');
end

function y = dynamics(t, X)
    gamma = 1.0;
    A = VectM([sin(t),cos(t);-cos(t),sin(t)]);
    dA = VectM([cos(t),-sin(t);sin(t),cos(t)]);
    I = [1;0;0;1];
    y = - dA*X - gamma*(A*X - I);
end

function vA = VectM(A)
    vA = [A(1,1), 0, A(1,2), 0;
          0, A(1,1), 0, A(1,2);
          A(2,1), 0, A(2,2), 0;
          0, A(2,1), 0, A(2,2)];
end